# Branch Protection Policy

## Purpose

This document establishes strict branch protection rules for the Python repository to ensure code quality and prevent unauthorized changes to production code.

---

## 🚨 PRIMARY RULE: AI AGENTS PROHIBITED FROM MODIFYING `main` BRANCH 🚨

### Absolute Prohibition

**AI agents, GitHub Copilot, and all automated code generation tools are STRICTLY FORBIDDEN from making any code changes to the `main` branch.**

### Scope of Prohibition

The following actions are **PROHIBITED** on `main` branch for AI agents:

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

---

## Branch Structure

### `main` Branch

- **Purpose**: Production-ready, stable code
- **Protection**: AI-agent modifications FORBIDDEN
- **Write Access**: Humans only
- **Merge Source**: Only from `testing` branch
- **Merge Authority**: Human developers only

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

- All merges from `testing` → `main` require human approval
- Humans verify changes before merging
- Humans maintain final authority over production code

### 4. Recommended GitHub Settings (Manual Setup Required)

To fully enforce this policy, repository admins should configure:

#### Branch Protection Rules for `main`

1. Navigate to: Repository Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require pull request reviews before merging
   - ✅ Require approvals: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators (optional but recommended)
   - ✅ Restrict who can push to matching branches
   - ✅ Do not allow bypassing the above settings

---

## Policy Violations

### Detection

- Code changes committed to `main` by AI agents
- Direct pushes to `main` from automated tools
- Bypassing branch protection workflows

### Response

1. **Immediate**: Revert unauthorized changes
2. **Investigation**: Review how policy was bypassed
3. **Correction**: Update AI instructions if needed
4. **Prevention**: Strengthen enforcement mechanisms

---

## Frequently Asked Questions

### Q: Can AI agents create pull requests to `main`?

**A:** No. AI agents should work exclusively on `testing`. Humans create PRs from `testing` to `main`.

### Q: What if AI agent is already on `main` when user requests changes?

**A:** AI agent MUST switch to `testing` before making any changes. If unable to switch, AI MUST refuse the request and ask human to switch branches.

### Q: Can AI agents read files from `main`?

**A:** Yes. Reading and analyzing code is allowed. Only modifications are prohibited.

### Q: What about hotfixes or critical bugs?

**A:** Even for urgent fixes:

1. AI makes fix on `testing` branch
2. Human reviews and tests
3. Human merges to `main`
This ensures all code is reviewed before production.

### Q: How do I enable GitHub branch protection?

**A:** See "Recommended GitHub Settings" section above. These must be configured by a repository administrator through GitHub's web interface.

---

## Document History

- **Created**: 2025-10-30
- **Purpose**: Establish AI agent restrictions on `main` branch
- **Authority**: Repository policy
- **Enforcement**: Documentation-based + recommended GitHub settings

---

## Summary

**ONE RULE TO REMEMBER:**

```
AI AGENTS: NEVER TOUCH `main` BRANCH
ALL AI CHANGES GO TO `testing` BRANCH
HUMANS MERGE `testing` → `main` AFTER REVIEW
```

This policy ensures:

- ✅ Code quality through human review
- ✅ Testing before production deployment
- ✅ Clear separation of development and production code
- ✅ Audit trail for all production changes
- ✅ Human oversight of critical code
