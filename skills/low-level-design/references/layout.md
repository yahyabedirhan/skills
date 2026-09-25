# Layout

Defaults for where modules go and what they are called; a repository's own conventions win.

- **Folders show the hierarchy.** Siblings are true peers: several implementations of one abstraction get their own subfolder beside the abstraction.
- **Generic apart from business code.** `utils/` holds code that could be pasted into any project and imports nothing else in the project. `helpers/` holds business logic two or more modules share. Adapters (routes, commands) only translate to and from the core.
- **Names say what a thing is, briefly.** Pick the name that can mean only one thing, and drop words its folder already says.
- **One file per resource or concern.** Small helpers of one kind share a file, and a module with one user lives inside it. Split a file when it mixes owners, not when it is long.
