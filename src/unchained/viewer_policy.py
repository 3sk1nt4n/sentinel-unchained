"""Strict, standard-library validation for the offline proof viewer."""

from __future__ import annotations

import re
from html.parser import HTMLParser

_SAFE_TAGS = frozenset(
    {
        "address",
        "article",
        "aside",
        "b",
        "bdi",
        "bdo",
        "blockquote",
        "body",
        "br",
        "caption",
        "cite",
        "code",
        "col",
        "colgroup",
        "dd",
        "details",
        "dfn",
        "div",
        "dl",
        "dt",
        "em",
        "figcaption",
        "figure",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "head",
        "header",
        "hgroup",
        "hr",
        "html",
        "i",
        "kbd",
        "li",
        "main",
        "mark",
        "meta",
        "nav",
        "ol",
        "p",
        "pre",
        "q",
        "rp",
        "rt",
        "ruby",
        "s",
        "samp",
        "section",
        "small",
        "span",
        "strong",
        "style",
        "sub",
        "summary",
        "sup",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "time",
        "title",
        "tr",
        "u",
        "ul",
        "var",
        "wbr",
    }
)
_VOID_TAGS = frozenset({"br", "col", "hr", "meta", "wbr"})
_HEAD_TAGS = frozenset({"meta", "style", "title"})
_URL_ATTRIBUTES = frozenset(
    {
        "about",
        "action",
        "archive",
        "attributionsrc",
        "background",
        "cite",
        "codebase",
        "data",
        "dynsrc",
        "formaction",
        "href",
        "imagesrcset",
        "itemid",
        "longdesc",
        "lowsrc",
        "manifest",
        "ping",
        "poster",
        "profile",
        "resource",
        "src",
        "srcdoc",
        "srcset",
        "usemap",
        "vocab",
        "xml:base",
        "xlink:href",
    }
)
_NONE_DIRECTIVES = frozenset(
    {
        "base-uri",
        "connect-src",
        "default-src",
        "font-src",
        "form-action",
        "frame-src",
        "img-src",
        "media-src",
        "object-src",
        "script-src",
    }
)
_CSP_DIRECTIVES = _NONE_DIRECTIVES | {"style-src"}
_CSS_ACTIVE_PATTERNS = (
    (re.compile(r"(?i)url\s*\("), "CSS url() is forbidden"),
    (re.compile(r"(?i)@import\b"), "CSS @import is forbidden"),
    (re.compile(r"(?i)expression\s*\("), "CSS expression() is forbidden"),
    (re.compile(r"(?i)(?:-webkit-)?image-set\s*\("), "CSS image-set() is forbidden"),
    (re.compile(r"(?i)@font-face\b"), "CSS @font-face is forbidden"),
    (re.compile(r"(?i)(?:behavior|-moz-binding)\s*:"), "active CSS bindings are forbidden"),
    (
        re.compile(r"(?i)\b(?:data|file|ftp|https?|javascript)\s*:"),
        "URL schemes are forbidden in CSS",
    ),
    (re.compile(r"[\\]"), "CSS escapes are forbidden"),
    (re.compile(r"/\*|\*/"), "CSS comments are forbidden"),
)


class _InertViewerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.stack: list[str] = []
        self.doctypes = 0
        self.html_elements = 0
        self.head_elements = 0
        self.body_elements = 0
        self.csp_values: list[str] = []
        self._style_chunks: list[str] = []
        self._inside_style = False
        self._html_closed = False

    def error(self, message: str) -> None:
        if message not in self.errors:
            self.errors.append(message)

    def handle_decl(self, decl: str) -> None:
        if decl.strip().casefold() != "doctype html":
            self.error("the only permitted declaration is <!doctype html>")
            return
        self.doctypes += 1
        if self.doctypes > 1:
            self.error("the document must contain exactly one doctype")
        if self.html_elements or self.stack:
            self.error("the doctype must precede the html element")

    def unknown_decl(self, _data: str) -> None:
        self.error("unknown declarations are forbidden")

    def handle_pi(self, _data: str) -> None:
        self.error("processing instructions are forbidden")

    def handle_comment(self, _data: str) -> None:
        self.error("HTML comments are forbidden in the proof viewer")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag not in _SAFE_TAGS:
            self.error(f"element <{tag}> is not permitted")
            return
        if self._html_closed:
            self.error("elements may not follow the closing html tag")

        self._validate_position(tag)
        attributes = self._validate_attributes(tag, attrs)
        if tag == "meta":
            self._validate_meta(attributes)

        if tag == "html":
            self.html_elements += 1
        elif tag == "head":
            self.head_elements += 1
        elif tag == "body":
            self.body_elements += 1

        if tag not in _VOID_TAGS:
            self.stack.append(tag)
        if tag == "style":
            self._inside_style = True
            self._style_chunks = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.casefold()
        if normalized not in _VOID_TAGS:
            self.error(f"non-void element <{normalized}> may not be self-closing")
            return
        self.handle_starttag(normalized, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in _VOID_TAGS:
            self.error(f"void element <{tag}> may not have an end tag")
            return
        if not self.stack:
            self.error(f"unexpected closing tag </{tag}>")
            return
        if self.stack[-1] != tag:
            self.error(f"mismatched closing tag </{tag}>; expected </{self.stack[-1]}>")
            return
        self.stack.pop()
        if tag == "style":
            self._inside_style = False
            self._validate_css("".join(self._style_chunks))
            self._style_chunks = []
        elif tag == "html":
            self._html_closed = True

    def handle_data(self, data: str) -> None:
        if "\x00" in data:
            self.error("NUL characters are forbidden")
        if self._inside_style:
            self._style_chunks.append(data)
        if data.strip() and "html" not in self.stack:
            self.error("non-whitespace text may not appear outside the html element")

    def close_and_validate(self) -> None:
        try:
            self.close()
        except Exception as exc:  # pragma: no cover - defensive HTMLParser boundary
            self.error(f"HTML parsing failed: {type(exc).__name__}: {exc}")
        if self.stack:
            self.error(f"unclosed elements remain: {self.stack}")
        if self.doctypes != 1:
            self.error("the document must contain exactly one <!doctype html>")
        if self.html_elements != 1:
            self.error("the document must contain exactly one html element")
        if self.head_elements != 1:
            self.error("the document must contain exactly one head element")
        if self.body_elements != 1:
            self.error("the document must contain exactly one body element")
        if len(self.csp_values) != 1:
            self.error("the document must contain exactly one CSP meta element")
        elif not self._valid_csp(self.csp_values[0]):
            self.error("the CSP does not match the inert proof-viewer policy")

    def _validate_position(self, tag: str) -> None:
        parent = self.stack[-1] if self.stack else None
        if tag == "html":
            if self.doctypes != 1:
                self.error("the html element must follow exactly one doctype")
            if parent is not None or self.html_elements:
                self.error("the html element must be the single document root")
            return
        if "html" not in self.stack:
            self.error(f"element <{tag}> is outside the html element")
            return
        if tag == "head":
            if parent != "html" or self.head_elements or self.body_elements:
                self.error("head must be the first unique direct child of html")
            return
        if tag == "body":
            if parent != "html" or self.head_elements != 1 or self.body_elements:
                self.error("body must be the unique direct child after head")
            return
        if parent == "html":
            self.error(f"only head and body may be direct children of html, not <{tag}>")
        if "head" in self.stack and tag not in _HEAD_TAGS:
            self.error(f"element <{tag}> is not permitted inside head")
        if "head" not in self.stack and "body" not in self.stack:
            self.error(f"element <{tag}> must be inside head or body")
        if parent in {"style", "title"}:
            self.error(f"element <{tag}> may not be nested inside {parent}")

    def _validate_attributes(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> dict[str, str | None]:
        normalized: dict[str, str | None] = {}
        for raw_name, value in attrs:
            name = raw_name.casefold()
            if name in normalized:
                self.error(f"element <{tag}> contains duplicate attribute {name!r}")
                continue
            normalized[name] = value
            if name == "style":
                self.error(f"inline style attributes are forbidden on <{tag}>")
            if name.startswith("on"):
                self.error(f"event-handler attribute {name!r} is forbidden")
            if name in _URL_ATTRIBUTES:
                self.error(f"URL-bearing attribute {name!r} is forbidden")
            if value is not None and "\x00" in value:
                self.error(f"attribute {name!r} contains a NUL character")
        return normalized

    def _validate_meta(self, attrs: dict[str, str | None]) -> None:
        if "head" not in self.stack:
            self.error("meta elements are permitted only inside head")
        http_equiv = (attrs.get("http-equiv") or "").strip().casefold()
        if http_equiv == "refresh":
            self.error("meta refresh is forbidden")
            return
        if http_equiv:
            if http_equiv != "content-security-policy":
                self.error(f"unsupported meta http-equiv value: {http_equiv!r}")
                return
            if set(attrs) != {"http-equiv", "content"}:
                self.error("the CSP meta element may contain only http-equiv and content")
            content = attrs.get("content")
            if not isinstance(content, str) or not content.strip():
                self.error("the CSP meta element requires nonempty content")
            else:
                self.csp_values.append(content)
            return
        if "charset" in attrs:
            if set(attrs) != {"charset"} or (attrs.get("charset") or "").casefold() != "utf-8":
                self.error("the charset meta element must be exactly utf-8")
            return
        if (attrs.get("name") or "").strip().casefold() == "viewport":
            if set(attrs) != {"name", "content"} or not attrs.get("content"):
                self.error("the viewport meta element requires only name and content")
            return
        self.error("unsupported meta element")

    def _validate_css(self, css: str) -> None:
        for pattern, message in _CSS_ACTIVE_PATTERNS:
            if pattern.search(css):
                self.error(message)

    @staticmethod
    def _valid_csp(value: str) -> bool:
        directives: dict[str, tuple[str, ...]] = {}
        for raw_directive in value.split(";"):
            parts = raw_directive.strip().casefold().split()
            if not parts:
                continue
            name, *sources = parts
            if name in directives:
                return False
            directives[name] = tuple(sources)
        if set(directives) != _CSP_DIRECTIVES:
            return False
        if directives.get("style-src") != ("'unsafe-inline'",):
            return False
        return all(directives.get(name) == ("'none'",) for name in _NONE_DIRECTIVES)


def validate_inert_viewer_html(text: str) -> tuple[str, ...]:
    """Return deterministic policy errors; an empty tuple means the HTML is inert."""

    if not isinstance(text, str):
        return ("viewer HTML must be text",)
    parser = _InertViewerParser()
    try:
        parser.feed(text)
    except Exception as exc:  # pragma: no cover - defensive HTMLParser boundary
        parser.error(f"HTML parsing failed: {type(exc).__name__}: {exc}")
    parser.close_and_validate()
    return tuple(parser.errors)


__all__ = ["validate_inert_viewer_html"]
