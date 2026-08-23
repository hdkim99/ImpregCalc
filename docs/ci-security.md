# CI routing and public-repository security

Audit date: 2026-08-23.

## DGX workflow

`.github/workflows/ci.yml` uses `push` to `main`, `pull_request` to `main`, and
manual `workflow_dispatch`. The self-hosted job has an explicit condition: a pull
request runs on persistent DGX hardware only when the actor is the repository owner
and the head repository is the same repository. Fork code and bot-authored pull
requests are not executed there.

The workflow does not use `pull_request_target`, `workflow_run`, `issue_comment`, or
a PR-head checkout under a privileged event. Top-level permission is only
`contents: read`; checkout does not persist credentials. Actions are pinned to full
commit SHAs.

## macOS workflow

External pull-request code may run only on ephemeral GitHub-hosted macOS runners.
The job has `contents: read`, receives no repository secrets, and does not use a
privileged trigger. This validates public contributions without exposing the DGX
host or a trusted local machine.

## Publish workflow

Publishing is triggered only by a GitHub release. The build job has `contents: read`.
The separate publish job obtains only `id-token: write`, is bound to the `pypi`
environment, downloads the build artifact, and uses PyPI Trusted Publishing. No
long-lived PyPI API token is specified.

