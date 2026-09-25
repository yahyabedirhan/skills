# Networking essentials

How the parts of a system talk to each other and to their callers: which protocol, how load is spread across servers, and how distance and failure are handled.

## Layers that matter

- **Network (L3)**: IP, addressing and routing. Taken as given.
- **Transport (L4)**: TCP, UDP, QUIC.
- **Application (L7)**: HTTP, REST, gRPC, SSE, WebSockets, WebRTC, DNS.

Each layer up adds latency and processing. A TCP connection is state both ends hold; setting one up per request costs round trips, which matters for persistent, real-time connections.

## Transport: TCP or UDP

TCP is connection-oriented, reliable and ordered, with flow and congestion control: the default, for nearly everything. UDP is connectionless and best-effort (no delivery or order guarantees) but faster: choose it when a late packet is worth less than a lost one (live video, games, VoIP, lossy telemetry), and when browsers aren't clients or get another path, since browsers support UDP only through WebRTC. Real products often mix them: TCP for signalling and auth, UDP for media.

## Application protocols

| Protocol | What it is | Use it for | Trade-off |
|---|---|---|---|
| HTTP / REST | Stateless request-response on resources | The default for APIs ([api-design.md](api-design.md)) | JSON is heavier than binary, rarely the bottleneck |
| GraphQL | One endpoint; the client asks for exactly the fields it needs | Many clients with different data needs, changing often | Query complexity and N+1 lookups on the server |
| gRPC | Binary RPC over HTTP/2 with Protocol Buffers and typed contracts | Internal service-to-service calls where speed matters | No browser support; weaker tooling for outside clients. REST outside, gRPC inside is a common split |
| SSE | One long HTTP response the server streams events into | Server-to-client push (live prices, notifications) | Connections drop; the client reconnects with the last event ID and the server must replay; some proxies buffer the stream |
| WebSockets | A persistent two-way connection, upgraded from HTTP | Frequent two-way traffic: chat, games, collaboration | Stateful connections are expensive at scale; every proxy and balancer on the path must support them |
| WebRTC | Peer-to-peer over UDP, via signalling, STUN and TURN servers | Audio and video calls | Complex; connections fail and fall back to relays |

For real-time needs, start with HTTP polling and move to SSE or WebSockets when polling stops meeting the requirement. Justify a WebSocket by a requirement; its infrastructure costs the most.

HTTP being stateless is what lets servers scale by adding more of them: minimize the stateful surface of a system. HTTPS encrypts the request but doesn't make its content trustworthy: never take the user's identity from the request body.

## Load balancing

Vertical scaling (a bigger machine) goes far with modern hardware ([numbers-to-know.md](numbers-to-know.md)); horizontal scaling (more machines) needs a way to spread requests.

- **Client-side**: the client reads a server list from a registry and picks a server itself; no extra hop. Fits a few clients you control (internal services; gRPC and Redis Cluster clients do this) or many clients that tolerate slow updates (DNS, which rotates IPs, bounded by its TTL).
- **Dedicated load balancer**: an extra hop, but instant updates to the server list and finer control.
  - **L4** routes connections without reading them; one TCP connection stays with one server. Use it for WebSockets and other persistent connections.
  - **L7** reads each HTTP request and can route on its path, headers or cookies. Use it for HTTP traffic.
- **Health checks** (a TCP connect, or an HTTP call expecting a 2xx) take failed servers out of rotation automatically; this is what makes a balancer an availability tool.
- **Algorithms**: round robin or random for stateless servers; least connections for servers holding persistent connections; IP hash for stickiness.
- Two balancers in different zones behind DNS remove the balancer as a single point of failure.

## Distance and regions

Light in fibre sets a floor: New York to London is at least ~56 ms round trip. Keep the data a request needs close together and close to the user.

- **CDN**: edge servers near users cache content; best for static media, also for cacheable, globally read responses ([caching.md](caching.md)).
- **Regional partitioning**: when users only touch local data (rides in one city), give each region its own servers and database, co-located.

## Failure

Assume every network call can fail, stall or return something unexpected.

- **Timeouts and retries** handle transient failures; retry with **exponential backoff and jitter**, so failing clients don't retry in lockstep.
- **Idempotency** makes retries safe: reads are naturally idempotent; writes carry an idempotency key the server checks before acting.
- **Circuit breakers** stop cascading failure: after repeated failures calls fail fast (open); after a pause a test call goes through (half-open) and, if it succeeds, traffic resumes (closed). They keep a recovering dependency from being flattened by retries (the thundering herd). Put them on calls to third parties, databases and other services.

---

Source: Hello Interview, [Networking Essentials](https://www.hellointerview.com/learn/courses/system-design/lesson/foundations/networking-essentials).
