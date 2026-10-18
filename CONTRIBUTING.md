# Contributing to TMDbHelper

Good contributions start with a clear problem and enough information to understand
it. Maintainer time is limited: keep reports, requests, and pull requests focused,
reproducible, and straightforward to review.

## Before opening an issue

- Update TMDbHelper to the latest version. Follow the [installation instructions](Readme.md#installation)
  to keep its dependencies up to date.
- Search existing issues, including closed issues, for the same bug or request.
  Add relevant information to an existing discussion instead of opening a duplicate.
- Check the [wiki](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/wiki)
  for existing functionality and usage instructions.
- Read the [AI usage policy](AI_USAGE.md).
- Use the appropriate issue template and complete its required fields.

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) to describe the
problem you actually encountered. Explain what you expected and what happened.

Provide exact steps that someone else can follow, including relevant settings.
For skinning issues, include the full `plugin://` path and/or the specific
`$INFO[]` values that are not working. Screenshots can help illustrate the problem,
but should accompany the information needed to reproduce it.

Upload your full `kodi.log` file, either as an attachment or through
[paste.kodi.tv](https://paste.kodi.tv/). See Kodi's
[log file locations](https://kodi.wiki/view/Log_file#Log_file_location) if needed.
Error reports require the full log; isolated error lines and selected snippets
leave out context needed to investigate. Reports without a full log will be closed.

Keep reproduction steps separate from supporting information. Describe observed
behaviour rather than presenting an unverified diagnosis as the cause.

## Requesting features

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml).
Explain what you want to happen, why it is needed, and which problem it solves.
A concrete example of your current workflow and the desired result helps establish
whether a feature is suitable.

If the request addresses an existing problem, include steps to reproduce that
problem. Add relevant screenshots or other supporting information where useful.
Keep the request focused so its scope and tradeoffs can be discussed clearly.

## Using AI tools

**Every AI-generated PR must link to a relevant bug report or feature request,
regardless of the size of the change.** Include the link in the PR description.

Read the [AI usage policy](AI_USAGE.md) before submitting AI-assisted reports or
pull requests. It explains the requirements for bug evidence, discussion of fixes,
and planning large features. Take responsibility for everything you submit and
keep explanations concise.

## Submitting pull requests

Keep each PR focused on one problem or agreed feature. Avoid unrelated refactors,
formatting changes, and speculative fixes that make the change harder to review.
For substantial features, discuss the scope and approach before investing in a
large implementation.

Follow the [coding conventions](AGENTS.md) and the architecture and style of nearby
code. Reuse existing abstractions, keep responsibilities small, and investigate
underlying errors instead of hiding them.

In the PR description:

- Link a relevant bug report or feature request in this repository. This is required
  for every PR, including those submitted through the API. Use `#123` or the full
  issue URL in the template's "Related issue or discussion" section. The issue must
  be labelled `bug` or `enhancement`; linking another PR does not qualify.
- Explain the problem, resulting behaviour, and why the approach addresses it.
- State what you tested, the results, and any remaining limitations.

Complete the "Related issue or discussion", "Problem and change", and
"Verification" sections of the PR template. The `PR policy` status checks these
sections and the linked issue. HTML comments do not count as completed sections.
Passing this check does not replace maintainer review of the issue's relevance,
the approach, or the verification performed.

Check syntax, whitespace, and affected routes and imports. Verify the changed
behaviour and relevant edge cases, and preserve existing behaviour outside the
intended change. Distinguish isolated checks from testing performed in Kodi; do
not claim Kodi verification unless you actually performed it. Do not add test
files to the codebase.

Be prepared to answer questions and revise the contribution during review.
