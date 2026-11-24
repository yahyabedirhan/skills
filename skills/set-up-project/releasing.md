# Releasing

This page explains how <project> releases a new version.
Read it before you start a release, and after you merge a pull request that changes the version, because a release is finished only when every step below is done.
The [`/set-up-project`](https://github.com/yahyabedirhan/skills/tree/main/skills/set-up-project) skill wrote it from the maintainer's shared release rules.

_`/set-up-project` fills in each part below from what the project does today, keeps each step to a line or two, and removes every note in italics like this one._
_Leave the version rule, the changelog format and the tag and notes formatting to the shared release rules, and write here only what this project does differently._

## What a release ships

This section names the parts that must all show the new version.

- _The version files, such as `package.json` or a `VERSION` file, and the packages that share one version._
- A tag, `v<version>`, and a GitHub release for it.
- A section in `CHANGELOG.md`.
- _The registry each package goes to, linked._

_When the project publishes to GitHub only, `/set-up-project` writes that in one sentence after the list._

## Branches

This section says where a version's work collects before it reaches `main`.

- The release branch, `release/<version>`, opens from `main` when work on the version starts.
- The version's pull requests target the release branch, and agents merge them there.
- The release pull request takes the release branch into `main`, and that merge waits for the maintainer's approval.

_`/set-up-project` keeps this section only when the maintainer chose a release branch in its Section E._

## Release order

This section lists the steps of every release, in order, so that a registry never gets a version without a tag and a GitHub release.

0. Check that the changelog, the version files, the latest tag and the latest GitHub release all name the same version, and finish any version that is behind first.
1. Open one release pull request that sets the version in _the version files_ and renames `## Unreleased` in `CHANGELOG.md` to `## <version> (<YYYY-MM-DD>)`.
   _With a release branch, make these changes on it, and open the release pull request from it into `main`._
   Before 1.0, a feature or a breaking change raises the middle number, and anything else raises the last number.
2. Ask the maintainer in chat, naming the release pull request, and merge it after they approve.
3. Tag the merged commit as `v<version>` and make its GitHub release, with the changelog section as the notes.
   _When a workflow does this, name the workflow instead._
4. _Publish to the registry, in the order the packages depend on each other, as 'Roles in a release' below says. Remove this step when the project publishes to GitHub only, and renumber the check._
5. Check again that every part names the new version.

## Roles in a release

This section names who does each step.

- The agent picks the version, writes the changelog, opens the release pull request, makes the tag and the GitHub release, and runs the checks.
- The maintainer approves the version and the merge.
  _Add any step that needs the maintainer's credentials, such as a publish with their two-factor code._
