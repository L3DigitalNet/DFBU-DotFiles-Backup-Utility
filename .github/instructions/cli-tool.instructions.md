---
description: "Custom instructions for CLI Tool development with Python"
applyTo: "**"
---

# CLI Tool Development Guidelines

*Note: All common requirements (file headers, testing, inline documentation) are defined in `copilot-instructions.md`. This file contains only CLI-specific requirements.*

## CLI Requirements
- **MUST** use `argparse` for argument parsing
- **MUST** implement proper exit codes (0=success, non-zero=error)
- **MUST** handle SIGINT (Ctrl+C) gracefully
- **MUST** support `--verbose`, `--quiet`, `--help`, `--version`
- **MUST** provide progress indicators for long operations
- **MUST** use logging levels appropriately
- **MUST** test argument parsing, exit codes, and interactive modes using pytest
- **MUST** validate CLI behavior through automated testing of command-line interfaces

## CLI-Specific Header Features
- **MUST** include CLI-specific Features section with:
  - Proper exit codes (0=success, non-zero=error)
  - Signal handling for graceful shutdown (SIGINT/Ctrl+C)
  - Standard CLI options: --verbose, --quiet, --help, --version
  - Progress indicators for long-running operations

## CLI Code Generation Focus
- **Framework:** Use `argparse`, `pathlib`, built-in `logging`
- **Architecture:** Separate parsing → validation → execution
- **Pattern:** Follow template below

## CLI Code Template

```python
def main() -> int:
    """Main entry point. Returns exit code."""
    # NOTE: Error handling deferred until v1.0.0 per main guidelines
    args = parse_arguments()
    setup_logging(args.verbose, args.quiet)
    return execute_command(args)

if __name__ == "__main__":
    sys.exit(main())
```
