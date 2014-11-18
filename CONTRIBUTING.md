**contributor guidelines**


When submitting a pull request (PR), or reviewing existing PR's in preparation for merge, please ensure the following criteria are met:

* PR relates to a prior filed issue, and the issue number is included in the body of the PR.
* The PR (not the issue) is targeted at the relevant milestone. If the PR is against master, target the current/latest milestone.
* The issue number is NOT in the title of the commit message. The issue MAY be included in the body of the commit message, but not the title.
* The PR title should be usable to populate the changelog.
* The PR description should clearly describe the functional change being made
* Unrelated functional changes are submitted separately.
* Note any limitations of the fix.
* Fix/feature being added has been coded in a similar style, or taken a similar logical pattern to the rest of the codebase.
* PR should, where possible, relate to a single issue
* All commits relating to a single issue in a PR are squashed to a single commit.
* The commit message and PR title should not contain typos
* The PR should be submitted against the correct branch. If the PR is against master, and the original issue was labeled with 'backport potential', 'cherry-pick -x' the issue from master into the relevant stable branch, and submit a separate PR to that branch

When submitting an issue, or working on an issue, please ensure the following criteria are met:

* The description clearly states or describes the original problem or root cause of the problem.
* Include historical information on how the problem was identified.
* Any relevant logs are included.
* If the issue is a bug that needs fixing in a branch other than Master, add the ‘backport potential’ tag TO THE ISSUE (not the PR).
* The provided information should be totally self-contained. External access to web services/sites should not be needed.
* If the issue is needed for a hotfix release, add the 'expedite' label.
* Steps to reproduce the problem if possible.
