# Session purposes

How each common purpose runs through the delivery framework. They are common cases, not the only options: a session can mix them, move from one to another (an explanation turning into a redesign), or be something else, so fit the framework to what the user asked for.

## Designing something new

Design it end to end from the user's spec: a complete first draft through every stage. Wherever the design has more than one reasonable option, let the user pick.

## Explaining existing code

Walk the code through the stages as it is, without changing it:

- Build each stage from the evidence: an existing design document (start there and check it against the code), the code itself (entry points, types, folders, tests), or the user's description. Cite the file behind each claim.
- Mark requirements you read from behaviour and tests as **inferred**. Mark what the code can't show, such as why a choice was made or what is planned, as **unknown**, and ask about it rather than filling it in.
- Show what each file owns and, where a file mixes several things, what it mixes. Report weaknesses as observations without proposing changes, since this session leaves the code as it is.
- Answer follow-up questions by tracing a call through the design.

## Redesigning existing code

1. Explain it as it is now, as above, and get the user's agreement that it's right.
2. Redesign it through the same stages, changing only what the redesign needs. A small change runs only the stages it touches; a restructure runs them all.
3. Show the before and after of every stage that changed, including the folder tree.

## Deciding one thing

Treat a question like "should this be an interface?" or "where does this module go?" as one decision. Answer it with the part of the design it touches, the requirement behind it, the options with their trade-offs, and a recommendation.
