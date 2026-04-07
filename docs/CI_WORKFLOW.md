[See docs/DISCLAIMER_SNIPPET.md](DISCLAIMER_SNIPPET.md)

# CI Workflow

The repository uses two distinct CI surfaces:

1. **✅ PR CI (`.github/workflows/pr-ci.yml`)** — canonical pull-request gate.
2. **🚀 Integration CI — Insight Demo (`.github/workflows/ci.yml`)** — full matrix for integration/release confidence.

## Triggers

### ✅ PR CI (canonical PR gate)
- `pull_request` targeting `main`
- `push` to `main`
- `merge_group`
- `workflow_dispatch`

Jobs:
- `Lint (ruff)`
- `Smoke tests`

### 🚀 Integration CI — Insight Demo (non-PR heavy matrix)
- `push` to `main`
- release tags: `v*`, `release-*`
- `workflow_dispatch`

This workflow intentionally does **not** run on `pull_request` or `merge_group`.
On `push` to `main`, it runs a **lean integration surface** (owner/actionlint, Linux lint+type and smoke-aligned pytest replay, docs-check).
On tags/manual dispatch it expands to the full release matrix (dual-version lint/type/test, docs build validation, Docker/signing/deploy path checks).
Mutation testing in `ci.yml` is config-driven: the workflow always runs `mutmut run` and relies on `[tool.mutmut]` in `pyproject.toml` (no legacy `--paths-to-mutate`/`--runner` flags) so mutmut CLI changes do not break merge runs. For merge safety the mutmut scope is intentionally bounded to `scripts/mutation_smoke_target.py`, uses explicit pytest test-selection fields, mutates covered lines only, and runs under a 20-minute timeout guard. The merge surface pins `mutmut==3.3.0` via `requirements-dev.lock`, and tests assert the lock pin and merge-safe config contract remain intact.
The merge-surface pytest/docs jobs also enforce an npm cache lifecycle contract: when `actions/setup-node` uses `cache: npm` with `NPM_CONFIG_CACHE`, the directory is created before setup-node and is not removed later in the job so setup-node's post-step cache save always has a valid, populated path.

## Branch protection (required checks)

Configure `main` branch protection with these required checks:

- `✅ PR CI / Lint (ruff)`
- `✅ PR CI / Smoke tests`

Keep **Require branches to be up to date** enabled.

Validate/enforce with:

```bash
python scripts/verify_branch_protection.py --apply --branch main
```

## CI health

The **🩺 CI Health** workflow hard-monitors `pr-ci.yml` (required PR gate) and evaluates `ci.yml` as a hard surface only when triggered by that workflow; scheduled/manual freshness checks for `ci.yml` are informational warnings. Missing-run dispatch remains enabled for scheduled/manual watchdog runs, but `workflow_run` executions are rerun-only (`--rerun-failed`) to avoid redundant dispatches when a concrete upstream run already exists. Self-monitoring is opt-in via `--include-self`, and workflow-run executions keep reruns enabled so Repo-Healer can move past run-attempt-1 report-only triage when failures persist.
`scripts/check_ci_status.py` also enforces this policy directly: when `GITHUB_EVENT_NAME=workflow_run`, `--dispatch-missing` is ignored so watchdog reruns never fan out into unrelated workflow dispatches.

Use:

```bash
python scripts/check_ci_status.py --wait-minutes 5 --pending-grace-minutes 45 --stale-minutes 90
# optional: add --dispatch-failed for explicit failed-run redispatches
```

After editing workflow files, run:

```bash
python tools/update_actions.py
pre-commit run --files .github/workflows/ci.yml .github/workflows/pr-ci.yml .github/workflows/ci-health.yml
```

## GitHub Actions runtime hygiene (Node 20 deprecation)

Workflow actions are pinned to Node24-compatible releases where currently available. A small number of third-party
actions still publish Node20 runtimes upstream (for example `softprops/action-gh-release@v2.6.1`), so those remain
pinned with explicit version comments until maintainers publish Node24 builds.
