"""Deterministic evidence-profile and custody tests with synthetic byte fixtures."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

import unchained.evidence as evidence_module
from unchained.caps import CapConfig, CapExceeded, CapKind, RunBudget
from unchained.evidence import (
    CustodyError,
    EvidenceDiscoveryError,
    EvidenceSession,
    MountContainmentError,
)


@pytest.fixture(autouse=True)
def disable_live_volatility_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep synthetic evidence tests offline even when Volatility is installed."""

    monkeypatch.setattr(evidence_module, "_volatility_base_command", lambda: None)


def test_classification_uses_content_instead_of_extension(tmp_path: Path) -> None:
    misleading_name = tmp_path / "definitely-not-memory.txt"
    misleading_name.write_bytes(b"PAGEDUMP" + bytes(4_096))

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()
        post_hashes = session.verify_custody()

    assert profile.os == "windows"
    assert profile.shape == "memory-only"
    assert profile.items[0].kind == "memory"
    assert post_hashes["definitely-not-memory.txt"] == profile.items[0].sha256


def test_filesystem_structure_routes_disk_and_emits_fs_key(tmp_path: Path) -> None:
    misleading_name = tmp_path / "looks-like-memory.vmem"
    content = bytearray(4_096)
    content[1_080:1_082] = b"\x53\xef"
    misleading_name.write_bytes(content)

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    assert profile.os == "linux"
    assert profile.shape == "disk-only"
    assert profile.fs == ("ext4",)
    assert profile.public_dict()["fs"] == ["ext4"]


def test_second_partition_offset_is_preserved_and_used_for_mount(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mount target must be the filesystem that classification actually matched."""

    first_offset = 2 * 512
    matched_offset = 16 * 512
    content = bytearray(matched_offset + 4_096)
    content[510:512] = b"\x55\xaa"
    for entry_index, start_sector in enumerate((2, 16)):
        entry = 446 + entry_index * 16
        content[entry + 4] = 0x83
        content[entry + 8 : entry + 12] = start_sector.to_bytes(4, "little")
        content[entry + 12 : entry + 16] = (4).to_bytes(4, "little")
    content[matched_offset + 1_080 : matched_offset + 1_082] = b"\x53\xef"
    image = tmp_path / "multi-partition.raw"
    image.write_bytes(content)

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    disk_item = profile.disk_items[0]
    assert disk_item.filesystem == "ext4"
    assert disk_item.filesystem_offset == matched_offset
    assert disk_item.filesystem_offset != first_offset
    assert disk_item.public_dict()["filesystem_offset"] == matched_offset

    captured: list[list[str]] = []
    monkeypatch.setattr(evidence_module, "_privileged_prefix", lambda: [])
    monkeypatch.setattr(
        evidence_module.shutil,
        "which",
        lambda name: "/usr/bin/mount" if name == "mount" else None,
    )

    def successful_mount(
        arguments: list[str],
        timeout: float = 120,
        budget: RunBudget | None = None,
    ) -> evidence_module._CommandResult:
        del timeout, budget
        captured.append(arguments)
        return evidence_module._CommandResult(returncode=0, output="")

    monkeypatch.setattr(evidence_module, "_run_fixed_command", successful_mount)
    monkeypatch.setattr(evidence_module, "_mount_is_read_only", lambda _path: True)
    monkeypatch.setattr(evidence_module, "_mount_is_active", lambda _path: False)
    mount = evidence_module._ReadOnlyMount()
    mount_path, warnings = mount.mount(
        disk_item.path,
        disk_item.filesystem,
        profile.os,
        disk_item.filesystem_offset,
    )

    assert mount_path is not None
    assert warnings == ()
    option_index = captured[0].index("-o") + 1
    assert f"offset={matched_offset}" in captured[0][option_index].split(",")
    assert f"offset={first_offset}" not in captured[0][option_index].split(",")
    assert mount.close() is True


def test_linux_version_text_log_is_not_promoted_to_memory(tmp_path: Path) -> None:
    """A printable kernel boot log must not become a synthetic memory image."""

    log = tmp_path / "boot-capture.bin"
    log.write_text(
        "Linux version 6.8.0-test (builder@example) #1 SMP PREEMPT\n"
        "2026-07-14T10:00:00 kernel: command line loaded\n"
        "2026-07-14T10:00:01 systemd[1]: starting services\n",
        encoding="utf-8",
    )

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    assert profile.os == "linux"
    assert profile.shape == "logs-only"
    assert profile.items[0].kind == "log"
    assert not profile.memory_items


def test_linux_version_log_cannot_create_a_disk_memory_os_conflict(tmp_path: Path) -> None:
    """Linux words in a log remain a weak hint beside strong Windows disk evidence."""

    disk = bytearray(4_096)
    disk[3:11] = b"NTFS    "
    (tmp_path / "windows-disk.raw").write_bytes(disk)
    (tmp_path / "boot.log").write_text(
        "Linux version 6.8.0-test (builder@example) #1 SMP\n"
        "kernel: captured from an unrelated host\n",
        encoding="utf-8",
    )

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    assert profile.os == "windows"
    assert profile.shape == "disk-only"
    assert {item.kind for item in profile.items} == {"disk", "log"}
    assert not any(warning.startswith("OS CONFLICT:") for warning in profile.warnings)


def test_linux_memory_without_symbols_is_unavailable_not_a_crash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = tmp_path / "capture.bin"
    memory.write_bytes(b"EMiL" + bytes(4_096))
    monkeypatch.setattr(evidence_module, "_volatility_base_command", lambda: None)
    monkeypatch.setattr(evidence_module, "_has_symbol_table", lambda _os, _budget=None: False)

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    assert profile.os == "linux"
    assert profile.shape == "memory-only"
    assert profile.items[0].available is False
    assert profile.items[0].symbols == "missing"
    assert "memory unavailable" in profile.capability_label.lower()


def test_logs_only_profile_does_not_advertise_an_unloadable_tool_family(tmp_path: Path) -> None:
    log = tmp_path / "artifact"
    log.write_text(
        "2026-01-01T00:00:00 systemd[1]: start\n"
        "2026-01-01T00:00:01 sshd[2]: login\n"
        "2026-01-01T00:00:02 kernel: audit(1)\n",
        encoding="utf-8",
    )

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    assert profile.shape == "logs-only"
    assert profile.available_tool_families == ()
    assert "no ready forensic tool family" in profile.capability_label


def test_post_run_full_hash_rejects_changed_evidence(tmp_path: Path) -> None:
    memory = tmp_path / "capture.bin"
    memory.write_bytes(b"PAGEDUMP" + bytes(4_096))
    session = EvidenceSession(tmp_path, mount=False, case_card_stream=None)
    session.profile()
    memory.write_bytes(b"PAGEDUMP" + b"changed" + bytes(4_089))

    try:
        with pytest.raises(CustodyError, match="custody verification failed"):
            session.verify_custody()
    finally:
        session.close()


def test_failed_tsk_probe_cannot_classify_filesystem_from_error_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = tmp_path / "opaque-image"
    image.write_bytes(b"not a filesystem")
    monkeypatch.setattr(
        evidence_module.shutil,
        "which",
        lambda name: "C:/fake/fsstat.exe" if name == "fsstat" else None,
    )
    monkeypatch.setattr(
        evidence_module,
        "_run_fixed_command",
        lambda _arguments, timeout=120, budget=None: evidence_module._CommandResult(
            returncode=1,
            output="File System Type: NTFS\nError: failed to inspect C:/cases/ntfs.e01",
        ),
    )

    filesystem, offsets, filesystem_offset = evidence_module._probe_filesystem_with_tsk(image)

    assert filesystem is None
    assert offsets == ()
    assert filesystem_offset is None
    assert (
        evidence_module._filesystem_from_text(
            "Error: failed to inspect C:/cases/ntfs.e01 as filesystem ntfs"
        )
        is None
    )


def test_tsk_probe_returns_the_partition_that_actually_matched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A later successful fsstat probe must not collapse to the first mmls offset."""

    image = tmp_path / "opaque-image.E01"
    image.write_bytes(b"opaque container")
    monkeypatch.setattr(
        evidence_module.shutil,
        "which",
        lambda name: f"C:/fake/{name}.exe" if name in {"fsstat", "mmls"} else None,
    )

    def fake_probe(
        arguments: list[str],
        timeout: float = 120,
        budget: RunBudget | None = None,
    ) -> evidence_module._CommandResult:
        del timeout, budget
        if arguments[0].endswith("mmls.exe"):
            return evidence_module._CommandResult(
                returncode=0,
                output=(
                    "000: Meta 0000000000 0000000000 0000000001 Primary Table (#0)\n"
                    "001: 000:000 0000000002 0000000005 0000000004 First\n"
                    "002: 000:001 0000000016 0000000031 0000000016 Second\n"
                ),
            )
        if "-o" not in arguments:
            return evidence_module._CommandResult(returncode=1, output="no filesystem at zero")
        sector = arguments[arguments.index("-o") + 1]
        if sector == "16":
            return evidence_module._CommandResult(
                returncode=0,
                output="File System Type: Ext4\n",
            )
        return evidence_module._CommandResult(returncode=1, output="not this partition")

    monkeypatch.setattr(evidence_module, "_run_fixed_command", fake_probe)

    filesystem, offsets, filesystem_offset = evidence_module._probe_filesystem_with_tsk(image)

    assert filesystem == "ext4"
    assert offsets == (2 * 512, 16 * 512)
    assert filesystem_offset == 16 * 512


def test_step_zero_obeys_the_run_wall_budget(tmp_path: Path) -> None:
    memory = tmp_path / "capture.bin"
    memory.write_bytes(b"PAGEDUMP" + bytes(4_096))
    now = 0.0

    def advancing_clock() -> float:
        nonlocal now
        now += 0.4
        return now

    budget = RunBudget(
        CapConfig(max_wall_seconds=1.0),
        clock=advancing_clock,
    )
    session = EvidenceSession(
        tmp_path,
        mount=False,
        case_card_stream=None,
        budget=budget,
    )

    try:
        with pytest.raises(CapExceeded) as raised:
            session.profile()
    finally:
        session.close()

    assert raised.value.kind is CapKind.WALL_SECONDS


def test_inventory_checks_wall_budget_for_each_entry(tmp_path: Path) -> None:
    for index in range(20):
        directory = tmp_path / f"dir-{index:02d}"
        directory.mkdir()
        (directory / "artifact").write_bytes(b"evidence")
    now = 0.0

    def advancing_clock() -> float:
        nonlocal now
        now += 0.05
        return now

    budget = RunBudget(CapConfig(max_wall_seconds=0.5), clock=advancing_clock)

    with pytest.raises(CapExceeded) as raised:
        evidence_module._enumerate_files(tmp_path, budget.check)

    assert raised.value.kind is CapKind.WALL_SECONDS


def test_inventory_fails_closed_when_walk_cannot_read_a_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An os.walk/scandir failure cannot silently omit part of the evidence set."""

    def failed_walk(
        _root: Path,
        *,
        followlinks: bool,
        onerror: object,
    ) -> tuple[()]:
        assert followlinks is False
        assert callable(onerror)
        onerror(PermissionError(13, "access denied", str(tmp_path / "sealed")))
        return ()

    monkeypatch.setattr(evidence_module.os, "walk", failed_walk)

    with pytest.raises(EvidenceDiscoveryError, match="Cannot enumerate evidence directory"):
        evidence_module._enumerate_files(tmp_path)


def test_session_rejects_a_symlink_as_the_top_level_evidence_path(tmp_path: Path) -> None:
    evidence_root = tmp_path / "real-evidence"
    evidence_root.mkdir()
    (evidence_root / "capture").write_bytes(b"PAGEDUMP" + bytes(4_096))
    link = tmp_path / "evidence-link"
    try:
        link.symlink_to(evidence_root, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"this host cannot create a directory symlink: {exc}")

    with pytest.raises(EvidenceDiscoveryError, match="may not be a symlink"):
        EvidenceSession(link, mount=False, case_card_stream=None)


def test_reference_mount_timeout_contains_owned_resources_before_cap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    disk = tmp_path / "disk"
    disk.write_bytes(b"disk")
    mountpoint = tmp_path / "mount"
    mountpoint.mkdir()
    now = 0.0
    budget = RunBudget(CapConfig(max_wall_seconds=1.0), clock=lambda: now)
    monkeypatch.setattr(evidence_module, "_loop_inventory", lambda _budget=None: {})
    monkeypatch.setattr(evidence_module, "_active_mounts_under", lambda _roots: ())
    worker = evidence_module._ReferenceMountWorker(disk, mountpoint)
    scratch = worker.scratch
    monkeypatch.setattr(worker, "_start", lambda: None)
    monkeypatch.setattr(worker, "_send", lambda _payload: None)

    def expire(_timeout: float) -> dict[str, object]:
        nonlocal now
        now = 2.0
        raise TimeoutError("synthetic worker timeout")

    monkeypatch.setattr(worker, "_reply", expire)

    with pytest.raises(CapExceeded) as raised:
        worker.mount("raw@0", budget)

    assert raised.value.kind is CapKind.WALL_SECONDS
    assert worker.close() is True
    assert not scratch.exists()


def test_reference_mount_timeout_fails_closed_when_mount_remains_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    disk = tmp_path / "disk"
    disk.write_bytes(b"disk")
    mountpoint = tmp_path / "mount"
    mountpoint.mkdir()
    monkeypatch.setattr(evidence_module, "_loop_inventory", lambda _budget=None: {})
    worker = evidence_module._ReferenceMountWorker(disk, mountpoint)
    monkeypatch.setattr(
        evidence_module,
        "_active_mounts_under",
        lambda _roots: (mountpoint,),
    )
    monkeypatch.setattr(evidence_module, "_privileged_prefix", lambda: None)

    with pytest.raises(MountContainmentError, match="resources active"):
        worker._contain_and_verify()

    assert worker.close() is False
    assert worker.scratch.exists()


def test_reference_mount_prelaunch_inventory_uses_remaining_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    disk = tmp_path / "disk"
    disk.write_bytes(b"disk")
    mountpoint = tmp_path / "mount"
    mountpoint.mkdir()
    scratch = tmp_path / "worker-scratch"
    now = 0.0
    budget = RunBudget(CapConfig(max_wall_seconds=1.0), clock=lambda: now)
    seen: list[RunBudget | None] = []

    def make_scratch(*, prefix: str) -> str:
        assert prefix == "unchained-mount-worker-"
        scratch.mkdir()
        return str(scratch)

    def expire_during_inventory(received: RunBudget | None = None) -> dict[str, Path]:
        nonlocal now
        seen.append(received)
        now = 2.0
        assert received is not None
        received.check()
        return {}

    monkeypatch.setattr(evidence_module.tempfile, "mkdtemp", make_scratch)
    monkeypatch.setattr(evidence_module, "_loop_inventory", expire_during_inventory)

    with pytest.raises(CapExceeded) as raised:
        evidence_module._ReferenceMountWorker(disk, mountpoint, budget)

    assert raised.value.kind is CapKind.WALL_SECONDS
    assert seen == [budget]
    assert not scratch.exists()


def test_reference_mount_worker_cannot_import_from_hostile_cwd_or_inherit_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    disk = tmp_path / "disk"
    disk.write_bytes(b"disk")
    mountpoint = tmp_path / "mount"
    mountpoint.mkdir()
    hostile = tmp_path / "unchained"
    hostile.mkdir()
    (hostile / "__init__.py").write_text("raise RuntimeError('shadowed')", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-cross-boundary")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("HTTPS_PROXY", "http://attacker.invalid")
    monkeypatch.setattr(evidence_module, "_loop_inventory", lambda _budget=None: {})
    monkeypatch.setattr(evidence_module, "_active_mounts_under", lambda _roots: ())
    captured: dict[str, object] = {}

    class FakeProcess:
        pid = 12345
        stdin = io.StringIO()
        stdout = io.StringIO()

        @staticmethod
        def poll() -> int:
            return 0

        @staticmethod
        def wait(timeout: float | None = None) -> int:
            del timeout
            return 0

    def fake_popen(command: list[str], **options: object) -> FakeProcess:
        captured["command"] = command
        captured.update(options)
        return FakeProcess()

    monkeypatch.setattr(evidence_module.subprocess, "Popen", fake_popen)
    worker = evidence_module._ReferenceMountWorker(disk, mountpoint)
    worker._start()

    environment = captured["env"]
    assert isinstance(environment, dict)
    assert captured["command"] == [
        evidence_module.sys.executable,
        "-P",
        "-m",
        "unchained.evidence",
        evidence_module._MOUNT_WORKER_ARGUMENT,
    ]
    assert captured["cwd"] == worker.scratch
    assert environment["PYTHONSAFEPATH"] == "1"
    assert "PYTHONPATH" not in environment
    assert "PYTHONHOME" not in environment
    assert "OPENAI_API_KEY" not in environment
    assert "HTTPS_PROXY" not in environment
    assert str(tmp_path) not in environment["PATH"]
    assert worker.close() is True


def test_fixed_probe_environment_strips_host_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-cross-boundary")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "must-not-cross-boundary")
    monkeypatch.setenv("HTTPS_PROXY", "http://credential.invalid")
    monkeypatch.setenv("PYTHONPATH", "hostile-import-path")

    environment = evidence_module._fixed_command_environment()

    assert "OPENAI_API_KEY" not in environment
    assert "AWS_SECRET_ACCESS_KEY" not in environment
    assert "HTTPS_PROXY" not in environment
    assert "PYTHONPATH" not in environment
    assert environment["PYTHONSAFEPATH"] == "1"
    assert environment.get("PATH")


def test_linux_symbols_must_resolve_this_evidence_plugin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = tmp_path / "memory"
    memory.write_bytes(b"EMiL" + bytes(4_096))
    disk = tmp_path / "disk"
    content = bytearray(4_096)
    content[1_080:1_082] = b"\x53\xef"
    disk.write_bytes(content)
    monkeypatch.setattr(evidence_module, "_volatility_base_command", lambda: ["vol"])
    monkeypatch.setattr(evidence_module, "_has_symbol_table", lambda _os, _budget=None: True)
    monkeypatch.setattr(
        evidence_module,
        "_run_fixed_command",
        lambda _arguments, timeout=120, budget=None: evidence_module._CommandResult(
            returncode=1,
            output="Unsatisfied requirement: kernel.layer_name; symbol table present",
        ),
    )

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    memory_item = next(item for item in profile.items if item.kind == "memory")
    disk_item = next(item for item in profile.items if item.kind == "disk")
    assert profile.os == "linux"
    assert profile.shape == "both"
    assert memory_item.symbols == "configured-unverified"
    assert memory_item.available is False
    assert memory_item.health == "unavailable-evidence-symbol-resolution-unverified"
    assert disk_item.available is True
    assert "memory unavailable" in profile.capability_label.lower()


def test_windows_failed_info_probe_is_routable_but_labeled_degraded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    memory = tmp_path / "memory"
    memory.write_bytes(b"PAGEDUMP" + bytes(4_096))
    monkeypatch.setattr(evidence_module, "_volatility_base_command", lambda: ["vol"])
    monkeypatch.setattr(
        evidence_module,
        "_run_fixed_command",
        lambda _arguments, timeout=120, budget=None: evidence_module._CommandResult(
            returncode=1,
            output="symbol download has not resolved this image",
        ),
    )

    with EvidenceSession(tmp_path, mount=False, case_card_stream=None) as session:
        profile = session.profile()

    item = profile.items[0]
    assert item.available is True
    assert item.symbols == "auto-download-pending"
    assert item.health == "degraded-windows-symbol-probe"
    assert "memory ready" not in profile.capability_label.lower()
    assert "auto-download/probe pending" in profile.capability_label
