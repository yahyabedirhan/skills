# Releasing

This page explains how this project releases a new version, from choosing the version number to checking that the release is complete.
Everyone who releases the project reads it, people and agents alike.
Read it before you start a release, and again after you merge a pull request that changes the version, because the release is not finished until every step below is done.
The `/set-up-project` skill wrote this page.
It started from the release rules that the maintainer shares across all of their projects, when such rules exist, and added what this project does in its own way.
When this page and the shared rules disagree, follow this page, and the next `/set-up-project` run brings the two back in line.

_`/set-up-project` fills in each part below from what the project does today, removes each section that does not apply, and removes every note in italics like this one._

## Version files

A release sets the new version in each of these files:

- `<file>` holds the version in `<the field or line>`.

_`/set-up-project` writes one line for each file that a release changes, such as `package.json`, a `VERSION` file or a constant in the source code._

## Release order

Every release runs these steps in this order, so that a registry never receives a version that has no tag and no GitHub release.

0. Start by catching up.
   Read what each part of the project says the newest version is:

   ```sh
   head -20 CHANGELOG.md | grep -m1 '^## [0-9]'
   git fetch --tags origin && git describe --tags --abbrev=0 origin/<default-branch>
   gh release view --json tagName -q .tagName
   <the registry's read, such as npm view <package> version>
   ```

   When one part is behind the others, finish that version first, from the first step it is missing, before you start a new version.
1. Open one pull request that sets the new version and the changelog.
   Choose the version from the commits since the last tag, set it in every version file, and rename `## Unreleased` to `## <version> (<YYYY-MM-DD>)`.
2. Merge the pull request once the maintainer approves it.
3. Tag the merged commit as `v<version>`, and make a GitHub release for that tag with the changelog section as its notes.
   _When a workflow does this, such as a `release.yml` that runs on a pushed tag, `/set-up-project` names the workflow here instead._
4. Publish the version to the project's registry, and name who runs each command.
   _`/set-up-project` writes how this project publishes, or removes this step when the project publishes only to GitHub._
5. Check the release by running the reads from step 0 again.
   Each read names the new version.

A version is complete when every part names it.
A release ends at step 5, not at the merge or the publish.

## Version rule

- Before version 1.0, a new feature or a breaking change raises the middle number and resets the last number to zero.
  Any other change raises the last number.
- From version 1.0, a breaking change raises the first number.
- A published version is never changed or reused.
  When a published version has a mistake, release a new patch version that fixes it.

## Changelog

- The changelog is `CHANGELOG.md` at the root of the repository, with the newest version first, written for the people who use the project.
- Each pull request that makes a change users can see adds its line under `## Unreleased` at the top of the changelog.

## Roles in a release

- The agent runs these steps: _`/set-up-project` lists them, such as choosing the version, writing the changelog, opening the pull request, tagging, making the GitHub release and running the checks._
- The maintainer runs these steps: _`/set-up-project` lists them, such as approving the merge, or a publish that needs the maintainer's two-factor code._
