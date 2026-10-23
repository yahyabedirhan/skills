# Releasing

How this project ships a version, for everyone who releases it. _(For `/set-up-project`: start from the user's shared release rules when the workstation repo has them, as step 2 says, and fill in what this project does today. Remove each section that doesn't apply, and each italic note.)_

## Where the version lives

- `<file>`: `<the field or line that holds the version>`. _(One line per file a release changes, such as `package.json`, a `VERSION` file or a source constant.)_

## Order

Every release runs these steps in this order, so a registry never gets a version that has no tag and no GitHub release:

0. **Catch up.** Read what each part says the newest version is:

   ```sh
   head -20 CHANGELOG.md | grep -m1 '^## [0-9]'
   git fetch --tags origin && git describe --tags --abbrev=0 origin/<default-branch>
   gh release view --json tagName -q .tagName
   <the registry's read, such as npm view <package> version>
   ```

   When one part is behind, finish that version first, from the first step it is missing, before a new version starts.
1. **Version and changelog**, in one pull request. Pick the version from the commits since the last tag, set it in every file above, and turn `## Unreleased` into `## <version> (<YYYY-MM-DD>)`.
2. **Merge**, after the maintainer approves it.
3. **Tag and GitHub release.** Tag `v<version>` on the merged commit, and make a GitHub release for the tag with the changelog section as its notes. _(Or the workflow that does it, such as `release.yml` on a pushed tag.)_
4. **Registry.** _(How this project publishes, and who runs each command. Remove the step when the project publishes nowhere but GitHub.)_
5. **Check.** Run the reads of step 0 again. Each one names the new version.

A version is done when every part names it. A release ends only at step 5, never at the merge or the publish.

## Version rule

- Before 1.0, a new feature or a breaking change raises the middle number and resets the patch. Anything else raises the patch.
- From 1.0, a breaking change raises the first number.
- A published version is never changed or reused. A mistake gets a new patch version.

## Changelog

- `CHANGELOG.md` at the root of the repository, newest first, written for a user of the project.
- Each pull request with a change a user can see adds its line under `## Unreleased` at the top.

## Who does what

- **The agent:** _(the steps an agent runs, such as the version, the changelog, the pull request, the tag, the GitHub release and the checks)_
- **The maintainer:** _(the steps only a person runs, such as approving the merge, or a publish that needs their two-factor code)_
