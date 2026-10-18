# AI usage in issue reports and pull requests

AI tools can assist with contributions, but generating text and code is only part
of the work. Reviewing a report, reproducing a bug, and planning a suitable change
take maintainer time. Keep submissions focused and verify what you submit.

## Required issue link

**Every AI-generated PR must link to a relevant bug report or feature request,
regardless of the size of the change.** Open or contribute to that issue before
submitting the PR, and include its link in the PR description. AI-generated PRs
without a relevant issue link may be closed.

The automated `PR policy` check requires an issue link for every PR, so enforcement
does not depend on identifying AI-generated contributions. Follow the
[PR submission requirements](CONTRIBUTING.md#submitting-pull-requests) for the
required issue labels and description sections.

## Bug reports

Describe the issue you encountered, provide steps to reproduce it, and upload your
full debug log. An AI diagnosis does not replace this information. Reports that
substitute AI speculation for a proper description and log may be closed.

## Bug fixes

Before submitting an AI-generated fix, open or contribute to a proper bug report.
The issue needs to be confirmed and reproduced, and appropriate fixes discussed,
before a PR is submitted. PRs that skip this process may be closed.

## Features

Discuss suitability and planning with the maintainer before submitting a large
AI-generated feature PR. Large submissions without that discussion may be closed.

## Your responsibility

Follow the repository's [coding conventions](AGENTS.md) when using AI tools to
generate or modify code.

Understand the code and claims you submit. Explain the relevant problem and
approach concisely. Long generated justifications do not establish that a diagnosis
is correct or that an implementation is appropriate.
