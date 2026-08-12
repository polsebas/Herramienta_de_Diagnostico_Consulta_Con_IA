# Project archived — August 2026

**Status:** archived / no further development  
**Decision date:** 2026-08-12  
**Last meaningful development:** September 2025

## Why we closed it

This repo started when coding agents and repo-aware assistants were less capable. The original bet — RAG + subagents + human-in-the-loop + Cursor task packs — made sense as an experiment.

By 2026, tools like **Cursor** (and similar coding agents) cover most of the day-to-day value with prompts and built-in repo context. Continuing this codebase as a product would mean competing with platforms that already ship execution, UX, and iteration speed we cannot match as a side project.

We are closing deliberately, not abandoning silently.

## Honest scope of what was built

What exists is largely a **prototype / spike**:

- Solid scaffolding around specs, HITL approvals, retrieval shapes, FastAPI team endpoints, and Agent UI wiring
- Many paths degrade to **simulation / fallback** when Milvus, ML, or an LLM client are missing
- Agno was listed as a dependency but the “team” layer is a custom coordinator with placeholder roles
- Documentation and roadmap often described enterprise goals and metrics that were **aspirational**, not production evidence

Treat historical “100% complete” or enterprise ROI claims in older docs as **obsolete narrative**, not current truth.

## What was worth learning

1. **Wedge over platform** — “report → editable roadmap → approved Cursor task packs with audit” is a sharper product idea than “enterprise RAG”.
2. **Simulation hides failure** — fallbacks that invent retrieval/LLM results make demos pass and products stall.
3. **Docs ≠ done** — measuring progress by merged PRs and file presence audits is not the same as a usable E2E path.
4. **Market timing** — a useful spike can be outpaced; archiving is a valid outcome.

## What you might still reuse (elsewhere)

If you extract anything into a new small kit, prefer these ideas over lifting the whole monorepo:

| Idea | Where it lived | Reuse note |
|------|----------------|------------|
| Task contracts (goal, risk, format, acceptance) | `app/spec_layer.py`, `app/specs/` | Keep the schema; drop ML classifiers |
| Human approval + audit trail | `app/human_loop.py`, `logs/audit.jsonl` | Keep the model; drop unfinished Slack/enterprise |
| Cursor task markdown templates | `app/cursor_tasks/`, docs examples | Useful as prompt/pack format |
| Preflight “needs configuration” | `app/analysis/preflight.py` | Simple UX pattern |

Do **not** port simulated Milvus/BM25, `advanced_contracts`, or the placeholder Agno roles as-is.

## How to archive on GitHub

After this closeout is merged to `main`:

1. Repo **Settings → General → Danger Zone → Archive this repository**
2. Optionally mark the description: `ARCHIVED — spike 2025; see ARCHIVE.md`

## Support

No new features, bugfixes, or roadmap work are planned. Issues and PRs should be closed as out of scope for an archived project.

Spanish version: [CIERRE.md](CIERRE.md)
