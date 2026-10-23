# Decisions

This folder records why each skill is the way it is, in one file per skill or topic, with dated entries.
These files are for maintaining the skills and are never installed.
A design in [../design/](../design/index.md) says how a skill is built now, and a decision says why.

## The shape of a file

```text
# Decisions: <skill or topic>

<one sentence: what this file decides>

## YYYY-MM-DD: <the choice, as a short sentence>

- **Status:** accepted | replaced by [<date>: <choice>](#<anchor>)
- **Context:** the problem or question, in one or two sentences.
- **Options:** each option considered, and why it lost. "None considered" when there was one way.
- **Choice and why:** the option chosen, and the reason.
- **Consequences:** what this changes or costs, and what stays open.

### References
- [<source>](https://...): <what it supports>
```

One entry is one choice. Every entry has the five fields, in this order. A field may hold sub-bullets. How-to steps are not decisions: they belong in the skill. A reversed decision keeps its old entry, with its status changed to `replaced by`, and gets a new entry whose Context says what it replaces. Copy the shape from the entries beside the one you add.
