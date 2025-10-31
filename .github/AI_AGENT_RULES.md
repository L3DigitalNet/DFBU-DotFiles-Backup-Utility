# AI Agent Rules - Quick Reference

## 🚨 RULE #1: NEVER MODIFY `main` BRANCH 🚨

### Before EVERY code change, run

```bash
git branch --show-current
```

### If output is `main`

```bash
git checkout testing
git branch --show-current  # Verify it says "testing"
```

### Only proceed with changes if on `testing` branch

---

## When to Stop and Ask Human

1. **Cannot determine current branch** → Ask human
2. **Cannot switch to `testing` branch** → Ask human
3. **User explicitly requests changes on `main`** → Refuse and explain policy
4. **Merge conflicts during branch switch** → Ask human
5. **Any uncertainty about branch** → Verify first

---

## Allowed Actions by Branch

| Action | `main` Branch | `testing` Branch |
|--------|---------------|------------------|
| Read files | ✅ Allowed | ✅ Allowed |
| Create files | ❌ FORBIDDEN | ✅ Allowed |
| Modify files | ❌ FORBIDDEN | ✅ Allowed |
| Delete files | ❌ FORBIDDEN | ✅ Allowed |
| Commit changes | ❌ FORBIDDEN | ✅ Allowed |
| Push changes | ❌ FORBIDDEN | ✅ Allowed |

---

## Standard Response Template

When asked to make changes while on `main`:

```
I cannot make code changes on the main branch per repository policy.
I need to switch to the testing branch first.

Let me verify the current branch and switch to testing:
[Run git commands to verify and switch]

Now I can proceed with your requested changes on the testing branch.
```

---

## Emergency Override

**There is NO emergency override.**

Even for critical bugs:

1. Make fix on `testing` branch
2. Human reviews
3. Human merges to `main`

---

## Full Policy

See: `.github/BRANCH_PROTECTION_POLICY.md` for complete details.
