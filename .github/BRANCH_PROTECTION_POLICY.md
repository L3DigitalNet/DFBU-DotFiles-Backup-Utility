# Branch Protection Policy

## Purpose

This document establishes branch protection rules for the Python repository to ensure code quality and prevent unauthorized changes to production code.

---

## 🚨 PRIMARY RULE: AI AGENTS PROHIBITED FROM AUTONOMOUSLY MODIFYING `main` BRANCH 🚨

### Absolute Prohibition

**AI agents, GitHub Copilot, and all automated code generation tools are STRICTLY FORBIDDEN from making any code changes to the `main` branch without explicit human approval.**

### Exception for Human-Initiated Merges

**EXCEPTION:** If the merge is initiated by a human using the `/merge_testing_to_main` command, AI agents are then permitted to modify the `main` branch as part of that merge process. This counts as explicit human approval for the specific merge operation.

### Scope of Prohibition

The following actions are **PROHIBITED** on `main` branch for AI agents (except during human-initiated `/merge_testing_to_main` command):

- ❌ Creating new files
- ❌ Modifying existing files
- ❌ Deleting files
- ❌ Renaming/moving files
- ❌ Any git commits
- ❌ Direct pushes
- ❌ Any code changes whatsoever

### Required Workflow for AI Agents

#### Before ANY Code Change

```bash
# 1. Check current branch (MANDATORY)
git branch --show-current

# 2. If on "main", immediately switch to "testing"
#    UNLESS currently executing a human-initiated /merge_testing_to_main command
if [ "$(git branch --show-current)" = "main" ]; then
    git checkout testing
fi

# 3. Verify you are on testing branch
git branch --show-current  # Output MUST be "testing"
```

#### Development Flow

1. **AI makes changes** → `testing` branch only
2. **Human reviews** → Tests, validates, approves
3. **Human merges** → `testing` → `main` (via PR or direct merge)
   - **During human-initiated `/merge_testing_to_main` command**: AI agents may modify `main` branch as part of the merge process

---

## Branch Structure

### `main` Branch

- **Purpose**: Production-ready, stable code
- **Protection**: AI-agent modifications FORBIDDEN (except during human-initiated `/merge_testing_to_main` command)
- **Write Access**: Humans only (except during human-initiated `/merge_testing_to_main` command)
- **Merge Source**: Only from `testing` branch
- **Merge Authority**: Human developers only, who may use `/merge_testing_to_main` command to authorize AI assistance

### `testing` Branch

- **Purpose**: Active development, testing, AI-assisted coding
- **Protection**: Open for AI agent modifications
- **Write Access**: AI agents and humans
- **Merge Destination**: Changes merge to `main` after human review

---

## Enforcement Mechanisms

### 1. Documentation-Based Enforcement

- Primary instructions in `.github/copilot-instructions.md`
- This policy document for reference
- Clear warning messages at top of instruction files

### 2. AI Agent Instructions

All AI assistants working in this repository MUST:

- Read and acknowledge this policy before making changes
- Verify branch before every file operation
- Switch to `testing` if on `main`
- Refuse to make changes if unable to switch branches

### 3. Human Review Process

- All merges from `testing` → `main` require human initiation and approval
- Humans verify changes before merging
- Humans maintain final authority over production code
- When humans use the `/merge_testing_to_main` command, this authorizes AI agents to perform the merge operations on the `main` branch
