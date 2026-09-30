# Existing systems

How to explain a system that already exists, and how to redesign one.

## Explaining

- Build each stage from the evidence at hand. If there is an existing design document, start there and check it against the code. In the code, read the routes and handlers, jobs and consumers, schemas and migrations, connection and deploy config, and calls to other services. The user's description is evidence too. Cite the file, section or message behind each claim.
- Mark requirements read from the code **inferred**. Mark what the evidence can't show, such as traffic, data sizes, incidents or why a choice was made, **unknown**, and ask about it rather than filling it in, so a guess never passes for a fact.
- In place of the deep dives, add a section on each concept the design relies on, such as its cache, its sharding or its consistency choice: what it is, why it matters for this design, and the trade-off the design made.
- Record weaknesses as observations, not proposals, because the session explains the system without changing it.
- Answer follow-up questions by walking a request or a failure through the design.

## Redesigning

Explain the system first, as above, and get the user's agreement that the explanation is right. Then redesign through the same stages, keeping each existing component unless the problem lies in it. In the deep dives, present the new design's trade-offs as options, as for a new system, and show every changed stage as a before/after `diff`.
