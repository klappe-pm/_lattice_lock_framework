# Contributing and Repo Management Policy

This repository uses a trunk-based, single-branch workflow. The only persistent branch is `main`. All changes land via Pull Requests (PRs) using squash merge.

## TL;DR
- Work in short-lived branches in your fork, open a PR to `main`, squash-merge, auto-delete branch.
- No direct pushes to `origin/main`. Local pre-push hook blocks non-`main` pushes to `origin`.
- CI must pass (tests, lint, typecheck) before merge.

## Why
- Keep history linear and readable (one commit per change on `main`).
- Avoid branch drift and stale remote branches.
- Make it easy for humans and AI agents to contribute safely.

## Branching
- Single permanent branch: `main`.
- Short-lived branches in forks only. Recommended naming: `{actor}/{ticket-or-issue}-{slug}`
  - Examples: `human/1234-doc-fix`, `claude/refactor-logger`, `gemini/ci-cache`, `devin/abc-bugfix`.

## Merge strategy
- Squash-and-merge only. Merge commits and rebase merges are disabled at the repository level.
- Auto-delete head branches on merge is enabled.

## Reviews and checks
- Open a PR for every change.
- At least one approving human review is recommended.
- All required checks must pass (tests, lint, typecheck). Add new checks as needed.

## Local safeguards
- A repo-scoped pre-push hook (in `.githooks/pre-push`) blocks pushing any branch except `main` to the canonical remote `origin`. It:
  - Allows tags and remote branch deletions.
  - Only enforces for `origin` (fork remotes are allowed).
  - Can be bypassed with `--no-verify` or `SKIP_BRANCH_POLICY=1` (not recommended).

## Working with AI/Agents
- Local tools (local LLMs, Claude Code, Gemini CLI): apply patches locally on a temp branch, push to your fork, open a PR.
- Chat tools (Claude, Gemini Chat): request diffs/patches, apply locally, then PR.
- Cloud-only (Devin.ai): operate exclusively in its own fork, open PRs back to this repo.

## Commit messages
- Conventional style preferred: `feat:`, `fix:`, `chore:`, `docs:`, etc.
- Keep the scope concise; body may include context and follow-up notes.

## Sync and cleanup helpers
- `git sync` fetches with prune and pulls with fast-forward only.
- `git prune-all` prunes deleted branches and tags across remotes.
- `git delete-merged` removes fully merged local branches (excluding `main`/`master`).

## Notes on enforcement
- Server-side branch protection may be limited on private repos without a paid plan. Local hook + reviews/checks via PRs provide practical enforcement.
- If/when server-side protections are available, enable: require PRs, linear history, conversation resolution, and 1+ approving review.

## Questions
Open an issue or start a discussion if the workflow needs adjustments.
