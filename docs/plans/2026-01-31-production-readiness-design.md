# Production Readiness Design

**Date:** 2026-01-31
**Status:** In Progress
**Last Updated:** 2026-02-01

## Overview

DFBU currently has solid architecture and performance, but lacks the safety guarantees needed for production use. This design defines a comprehensive reliability layer built in **risk-first order**.

### Version History

| Version | Release Date | Features |
|---------|--------------|----------|
| v0.6.0 | (untagged) | P0: Pre-restore safety |
| v0.7.0 | 2026-02-01 | YAML config migration, CLI removal, config directory removal |

### Remaining Roadmap

| Priority | Feature | Risk Mitigated | Version |
|----------|---------|----------------|---------|
| **P0** | Pre-restore safety | Data loss - overwriting files with no way back | ✅ Done |
| **P1** | Backup verification | Silent failures - thinking backups succeeded when they didn't | v0.8.0 |
| **P2** | Error handling | Confusion & partial states - unclear what went wrong or how to fix it | v0.9.0 |

### Design Principles

1. **Non-breaking** - All features additive; existing workflows unchanged
2. **Opt-out not opt-in** - Safety features enabled by default
3. **Transparent** - Users can see exactly what safety measures happened
4. **Testable** - Each feature gets comprehensive test coverage before merge

---

## P0: Pre-Restore Safety ✅ COMPLETE

### Problem

When restoring dotfiles, DFBU overwrites existing files without any backup. If the restore goes wrong (wrong version, corrupted backup, user error), the original files are gone forever.

### Solution: Automatic Pre-Restore Backup

Before any restore operation, copy all files that will be overwritten to a timestamped backup location.

### Storage Location

```
~/.local/share/dfbu/restore-backups/
└── 2026-01-31_143052/           # Timestamp of restore operation
    ├── manifest.toml            # What was backed up and why
    ├── .bashrc                  # Flat file backup
    ├── .config/
    │   └── konsole/
    │       └── konsolerc        # Preserves directory structure
    └── ...
```

### Manifest Format

```toml
[restore_operation]
timestamp = "2026-01-31T14:30:52"
source_backup = "/backups/mirror/hostname/2026-01-28/"
hostname = "workstation"
file_count = 12

[[backed_up_files]]
original_path = "~/.bashrc"
backup_path = ".bashrc"
size_bytes = 4096
modified = "2026-01-15T09:22:11"
```

### Retention Policy

- Keep last **5 restore backups** by default (configurable)
- Automatic cleanup of oldest when limit exceeded
- Never delete during a restore operation (cleanup happens at start of next restore)

### Integration Points

- `BackupOrchestrator.restore()` - Add pre-backup step before any file operations
- New `RestoreBackupManager` component following existing Protocol pattern
- Config option: `[options] pre_restore_backup = true` (default: true)
- Config option: `[options] max_restore_backups = 5`

### Implementation Steps

1. Create `RestoreBackupManager` component + `RestoreBackupManagerProtocol`
2. Add manifest TOML read/write
3. Integrate into `BackupOrchestrator.restore()`
4. Add retention/cleanup logic
5. Wire config options to UI (Configuration tab)
6. Comprehensive tests

---

## P1: Backup Verification (v0.8.0)

### Problem

Currently, backups can fail silently. A file copy might succeed but produce a corrupted result, or a tar archive might be incomplete. Users have no way to know if their backups are trustworthy.

### Solution: Multi-Level Verification

Three verification checks, each catching different failure modes:

| Check | What It Catches | When |
|-------|-----------------|------|
| **Existence** | Missing files, failed writes | After each file/archive |
| **Size match** | Truncated copies, incomplete writes | After each file/archive |
| **Hash comparison** | Bit-level corruption, subtle errors | Optional, per-operation or scheduled |

### Verification Flow (Mirror Backup)

```
For each dotfile:
  1. Copy file to destination
  2. Verify destination exists
  3. Compare source size == destination size
  4. If hash_verify enabled: compare SHA-256 hashes
  5. Record result in verification report
```

### Verification Report

After each backup, generate a verification summary:

```toml
[verification]
timestamp = "2026-01-31T15:00:00"
backup_type = "mirror"
total_files = 24
verified_ok = 23
verified_failed = 1
hash_verified = true

[[results]]
path = "~/.bashrc"
status = "ok"
size_match = true
hash_match = true

[[results]]
path = "~/.config/nvim/init.lua"
status = "failed"
error = "size_mismatch"
expected_size = 8192
actual_size = 4096
```

### UI Integration

- Progress bar shows verification step: "Verifying... (23/24)"
- Summary in log panel: "✓ 23 files verified, ✗ 1 failed"
- Failed verifications highlighted in red with details
- New "Verify Existing Backup" button to check previous backups on-demand

### Config Options

```toml
[options]
verify_after_backup = true      # Always verify (default: true)
hash_verification = false       # SHA-256 check (default: false, slower)
```

### Implementation Steps

1. Create `VerificationManager` component + `VerificationManagerProtocol`
2. Implement size/hash verification functions
3. Integrate into backup workflow (mirror + archive)
4. Add verification report generation
5. Add "Verify Backup" UI button
6. Progress/status UI updates
7. Comprehensive tests

---

## P2: Error Handling & Recovery (v0.9.0)

### Problem

Current error handling is basic - operations stop on first error with limited context. Users can't tell what succeeded, what failed, or how to fix it. Partial backups leave the system in unclear states.

### Solution: Structured Error Handling with Recovery Options

### Error Categories

| Category | Examples | Handling |
|----------|----------|----------|
| **Recoverable** | Permission denied, disk full, file locked | Retry option, skip option, continue with others |
| **Non-recoverable** | Source missing, config corrupt | Clear message, safe abort, preserve completed work |
| **Warnings** | Symlink followed, empty directory | Log and continue, summarize at end |

### Operation Result Model

Every operation returns a structured result, not just success/fail:

```python
@dataclass
class OperationResult:
    status: Literal["success", "partial", "failed"]
    completed: list[PathResult]      # What succeeded
    failed: list[PathResult]         # What failed and why
    skipped: list[PathResult]        # What was skipped and why
    warnings: list[str]              # Non-fatal issues
    can_retry: list[Path]            # Failed items that might succeed on retry
```

### User-Facing Error Messages

Replace technical errors with actionable messages:

| Before | After |
|--------|-------|
| `PermissionError: [Errno 13]` | "Cannot read ~/.ssh/config - permission denied. Run with elevated permissions or skip this file?" |
| `FileNotFoundError` | "Source file ~/.bashrc no longer exists. It may have been deleted since the config was loaded." |
| `OSError: No space left` | "Backup drive is full (needs 2.4 MB, only 1.1 MB free). Free space or choose a different destination." |

### Recovery UI

When errors occur during backup/restore:

```
┌─ Backup Interrupted ──────────────────────────────┐
│                                                   │
│  ✓ 18 files backed up successfully                │
│  ✗ 2 files failed                                 │
│                                                   │
│  Failed:                                          │
│    ~/.ssh/config - Permission denied              │
│    ~/.gnupg/pubring.kbx - File locked             │
│                                                   │
│  [ Retry Failed ]  [ Skip & Continue ]  [ Abort ] │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Implementation Steps

1. Create `ErrorHandler` component + `ErrorHandlerProtocol`
2. Define `OperationResult` dataclass in `common_types.py`
3. Wrap file operations with structured error handling
4. Create recovery dialog UI (`.ui` file)
5. Add retry/skip/continue logic
6. Update all operations to return structured results
7. Comprehensive tests

---

## P3: File Size Management (v1.0.0)

### Problem

DFBU is designed for backing up dotfiles and configuration files, typically small text files suitable for Git storage. However, some applications create large configuration directories with caches, databases, profiles, and binary data that can quickly exceed Git repository size limits (typically 1-5 GB):

- Browser profiles (Firefox, Chrome) can be hundreds of MB to several GB
- IDE settings with cached indexes (VS Code, Cursor)
- Application data directories (Flatpak, Docker Desktop)
- Databases (Akonadi, KWallet)
- Cache directories mixed with actual config files

### Solution: File Size Monitoring and Warnings

Implement size checks during backup operations with user warnings and optional exclusion patterns.

### Size Thresholds

| Level | Size | Action |
|-------|------|--------|
| **Info** | < 10 MB | No warning, log only |
| **Warning** | 10-100 MB | Yellow warning in UI, continue |
| **Alert** | 100 MB - 1 GB | Orange alert, recommend exclusion |
| **Critical** | > 1 GB | Red alert, block by default with override option |

### Size Check Points

1. **Pre-backup scan** - Analyze total size before starting
2. **Per-file check** - Warn during backup if individual file exceeds threshold
3. **Directory size** - Calculate directory totals before backing up
4. **Post-backup report** - Summary of total backup size and largest items

### Size Report Example

```toml
[size_analysis]
timestamp = "2026-01-31T16:00:00"
total_files = 245
total_size_bytes = 524288000  # 500 MB
largest_items = [
    { path = "~/.mozilla/firefox/profile", size = 450000000, type = "dir" },
    { path = "~/.config/Code/CachedData", size = 35000000, type = "dir" },
    { path = "~/.local/share/akonadi", size = 28000000, type = "dir" }
]

[warnings]
items_over_100mb = 1
items_over_10mb = 3
items_over_1gb = 0
```

### Exclusion Patterns

Add `.dfbuignore` support (similar to `.gitignore`):

```
# Exclude cache directories
**/Cache/
**/CachedData/
**/.cache/

# Exclude large browser data
**/.mozilla/firefox/*/cache2/
**/.config/google-chrome/*/Cache/

# Exclude databases
**/*.sqlite-shm
**/*.sqlite-wal
```

### UI Integration

Pre-backup size warning dialog:

```
┌─ Large Files Detected ────────────────────────────┐
│                                                   │
│  ⚠️  Your backup contains large files:            │
│                                                   │
│  ~/.mozilla/firefox/profile      450 MB          │
│  ~/.config/Code/CachedData       35 MB           │
│  ~/.local/share/akonadi          28 MB           │
│                                                   │
│  Total backup size: 500 MB                        │
│  Recommended for Git: < 100 MB                    │
│                                                   │
│  Recommendation: Exclude cache/data directories   │
│                                                   │
│  [ Create Exclusions ]  [ Continue Anyway ]       │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Config Options

```toml
[options]
# Size checking (v0.9)
size_check_enabled = true
size_warning_threshold_mb = 10
size_alert_threshold_mb = 100
size_critical_threshold_mb = 1024
auto_exclude_cache = true        # Automatically skip **/cache/** directories
```

### Smart Exclusion Suggestions

Analyze common patterns and suggest exclusions:

```python
COMMON_EXCLUDES = {
    "cache": ["**/cache/", "**/.cache/", "**/Cache/"],
    "logs": ["**/logs/", "**/*.log"],
    "temp": ["**/tmp/", "**/temp/", "**/.tmp/"],
    "binary": ["**/*.so", "**/*.dll", "**/*.exe"],
    "databases": ["**/*.db-wal", "**/*.db-shm", "**/cache2/"],
}
```

### Implementation Steps

1. Create `SizeAnalyzer` component + `SizeAnalyzerProtocol`
2. Implement directory/file size calculation with progress
3. Define size thresholds and warning levels
4. Create size report generation
5. Add `.dfbuignore` parser and pattern matching
6. Build warning dialog UI (`.ui` file)
7. Add "Create Exclusions" helper to auto-generate `.dfbuignore`
8. Integration with pre-backup workflow
9. Config options in UI
10. Comprehensive tests
11. Documentation updates

---

## Components Overview

| Component | File | Protocol | Purpose |
|-----------|------|----------|---------|
| `RestoreBackupManager` | `restore_backup_manager.py` | `RestoreBackupManagerProtocol` | Pre-restore backups, retention, manifest I/O |
| `VerificationManager` | `verification_manager.py` | `VerificationManagerProtocol` | Hash comparison, size checks, report generation |
| `ErrorHandler` | `error_handler.py` | `ErrorHandlerProtocol` | Error categorization, message formatting, recovery coordination |
| `SizeAnalyzer` | `size_analyzer.py` | `SizeAnalyzerProtocol` | File/directory size analysis, exclusion patterns, size reports |

All components follow the existing patterns:
- Pure Python in model layer (no Qt imports)
- Protocol-based dependency injection
- Integration through `DFBUModel` facade
- Worker threads for long operations

---

## Configuration Summary

```toml
[options]
# Pre-restore safety (v0.6) ✅
pre_restore_backup = true
max_restore_backups = 5

# Verification (v0.8)
verify_after_backup = true
hash_verification = false

# Error handling (v0.9) - no config options, always enabled

# File size management (v1.0)
size_check_enabled = true
size_warning_threshold_mb = 10
size_alert_threshold_mb = 100
size_critical_threshold_mb = 1024
auto_exclude_cache = true
```

---

## Release Milestones

### v0.6.0 - Pre-Restore Safety ✅ COMPLETE

- [x] `RestoreBackupManager` component
- [x] `RestoreBackupManagerProtocol` interface
- [x] Manifest TOML read/write
- [x] Integration with `BackupOrchestrator.restore()`
- [x] Retention/cleanup logic
- [x] Config options in UI
- [x] Comprehensive tests
- [x] Documentation updates

### v0.7.0 - Infrastructure Updates ✅ COMPLETE

- [x] YAML config format migration (from TOML)
- [x] CLI removal (GUI-only application)
- [x] Config directory selection removal (fixed path)

### v0.8.0 - Backup Verification
- [x] `VerificationManager` component
- [x] `VerificationManagerProtocol` interface
- [x] Size verification
- [x] Hash verification (SHA-256)
- [x] Verification report generation
- [x] "Verify Backup" UI button
- [x] Config options (`verify_after_backup`, `hash_verification`)
- [x] Comprehensive tests (30 test cases)
- [x] Documentation updates

### v0.9.0 - Error Handling & Recovery
- [ ] `ErrorHandler` component
- [ ] `ErrorHandlerProtocol` interface
- [ ] `OperationResult` dataclass
- [ ] Error categorization logic
- [ ] User-friendly error messages
- [ ] Recovery dialog UI
- [ ] Retry/skip/continue logic
- [ ] Comprehensive tests
- [ ] Documentation updates

### v1.0.0 - File Size Management
- [ ] `SizeAnalyzer` component
- [ ] `SizeAnalyzerProtocol` interface
- [ ] Directory/file size calculation
- [ ] Size threshold warnings
- [ ] `.dfbuignore` parser
- [ ] Warning dialog UI
- [ ] Smart exclusion suggestions
- [ ] Pre-backup size scan
- [ ] Size report generation
- [ ] Config options in UI
- [ ] Comprehensive tests
- [ ] Documentation updates

### v1.1.0 - Production Ready

- [ ] All reliability features complete (P0-P3)
- [ ] Full test coverage across all components
- [ ] Documentation complete
- [ ] Release notes
- [ ] Version bump and tag
