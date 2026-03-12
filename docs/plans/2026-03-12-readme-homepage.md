# README Homepage Refresh Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite the repository README into a stronger GitHub homepage that combines open-source clarity with the real machine-migration workflow this tool is built for.

**Architecture:** Keep the project behavior unchanged and focus only on restructuring the README. The new document will lead with the problem and value proposition, then move through commands, artifacts, workflow, safety, and roadmap in a public-facing format.

**Tech Stack:** Markdown

---

### Task 1: Rewrite the README structure

**Files:**
- Modify: `README.md`

**Step 1: Draft the new top sections**

Add the title, tagline, badges, and "Why" section so the repository immediately explains its purpose.

**Step 2: Add command overview and quick start**

Document `backup`, `release`, `restore`, and `doctor` with concise examples that match the CLI.

**Step 3: Add artifacts and workflow sections**

Explain the output files and show the old-Mac to new-Mac flow.

**Step 4: Add safety, roadmap, and license sections**

Keep the safety model explicit and close with the roadmap and existing license.

### Task 2: Verify README accuracy

**Files:**
- Modify: `README.md`

**Step 1: Re-read commands against implementation**

Check that the README examples match the current CLI and wrapper scripts.

**Step 2: Run repository verification**

Run: `pytest -q`
Expected: PASS with the existing test suite still green.

**Step 3: Inspect git diff**

Run: `git diff -- README.md`
Expected: only the intended README rewrite appears.

### Task 3: Prepare for commit

**Files:**
- Modify: `README.md`

**Step 1: Review the final README once more**

Confirm that the README reads cleanly as a GitHub homepage and stays concise.

**Step 2: Commit with docs-focused message**

```bash
git add README.md
git commit -m "docs(readme): refresh github homepage"
```
