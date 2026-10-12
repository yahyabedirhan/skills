# Profiles

The diagram-design profiles this skill ships. Each one is a full style guide.

| Profile | File | Use it for |
|---|---|---|
| Cursor Dark (default) | [cursor-dark.md](cursor-dark.md) | every diagram, unless another profile fits better |

## The shape of a profile

A profile follows diagram-design's profile format, as upstream [profiles.md](https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/profiles.md) defines it: one metadata comment, then the full style guide. Name the file `<slug>.md`, with a slug of lowercase letters, digits and hyphens.

```markdown
<!-- diagram-design-profile
name: <display name>
slug: <slug, same as the file name>
source-url: <url or none>
created: YYYY-MM-DD
updated: YYYY-MM-DD
notes: <one line, or none>
-->
# Style Guide

## Tokens
### Semantic roles        # table: Role | Purpose | Default (light) | Default (dark)
## Typography             # table of role keys and font families
### Font source           # a `Font source:` line, web or system
```

Keep every row of the upstream `### Semantic roles` and `## Typography` tables, since diagram-design fills a missing row from its defaults and warns. The other style-guide sections are optional. Add a row to the table above for each new profile.
