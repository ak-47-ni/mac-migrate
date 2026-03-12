# README Homepage Refresh Design

**Goal**
Upgrade the GitHub homepage README so it reads like a polished open-source project page while still reflecting the real developer pain point it solves: migrating a macOS development environment to a new machine.

## Approved direction
- Use a hybrid style: open-source project page + real-world developer workflow.
- Keep the tone practical and professional, with a small amount of programmer empathy.
- Focus on README structure and content quality first.
- Do not add screenshots, GIFs, or new product features in this iteration.

## Audience
- Developers landing on the GitHub repo for the first time.
- The repository owner using the project as a real migration tool.
- Contributors who need to quickly understand the project scope and safety model.

## Problems with the current README
- It is accurate but too short for a public project homepage.
- It lacks a strong top-level value proposition.
- It does not explain the migration workflow end-to-end.
- It does not clearly distinguish safe migration from full machine cloning.
- It does not surface release artifacts such as `SHA256SUMS.txt` and `release.json` early enough.

## Target structure
1. Title and one-sentence tagline
2. Badges (`GPL-3.0`, `Python 3.8+`, `macOS`)
3. Why this project exists
4. Core commands and what they do
5. Quick start
6. Release artifacts and what each file means
7. Typical old-Mac to new-Mac workflow
8. Safety model
9. Roadmap
10. License

## Content rules
- Keep sections short and scannable.
- Prefer concrete command examples over abstract explanations.
- Explain the difference between `backup`, `release`, `restore`, and `doctor` clearly.
- Call out that the tool does not migrate secrets, SSH keys, or login sessions.
- Keep command examples aligned with the current CLI implementation.

## Non-Goals
- No screenshots or animated demos in this pass.
- No contribution guide, issue templates, or CI badges in this pass.
- No code changes unless documentation verification reveals a mismatch.

## Verification
- Re-read the updated README for clarity and consistency.
- Confirm command examples match the current CLI entrypoints.
- Run the existing test suite after the docs update to ensure no accidental repo changes slipped in.
