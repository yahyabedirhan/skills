# API design

The contract between the system and its callers, produced in the API stage of the delivery framework. A reasonable API is the goal, not a perfect one: design the user-facing endpoints, then move on to the harder parts. Internal APIs get one line in the high-level design ("services talk over gRPC").

## Choosing the protocol

- **REST**: resources identified by URLs, manipulated with HTTP methods. The default; it fits most web and mobile APIs.
- **GraphQL**: one endpoint where clients ask for exactly the data they need. Choose it when clients with different needs (a mobile app and a dashboard) would otherwise force many endpoints or over-fetching. Costs: the N+1 problem (one query for a list, one per item, solved with batching), field-level authorization, harder caching.
- **RPC (gRPC)**: action-oriented calls with binary serialization and generated, typed clients. Choose it for internal service-to-service calls where performance or cross-language types matter, or when an action doesn't fit a resource (`checkPermission(user, resource)`).

Real-time updates use SSE or WebSockets, which are persistent connections rather than traditional APIs ([networking-essentials.md](networking-essentials.md)).

## REST resources

Resources are the core entities, as plural nouns: things in the system, not actions (`POST /events/{id}/bookings`, not `/bookEvent`).

- **Path parameters** identify a specific resource, and are required (`/events/{id}`).
- **Query parameters** filter, sort and paginate, and are optional (`/tickets?event_id=1&section=VIP`).
- **The request body** carries the data being created or changed.

Nest a resource under its parent (`/events/{id}/tickets`) when the parent is always required; use a query parameter when it's one optional filter among many.

**Methods and idempotency** (repeating the request leaves the server in the same state): GET reads and is idempotent; POST creates and isn't; PUT replaces and is; PATCH updates part and is idempotent only when written as "set", not "append"; DELETE is idempotent even though the second call returns 404. Idempotency matters because clients retry after network failures.

Status codes: the common ones are enough; the distinction that matters is 4xx (the client's fault) against 5xx (the server's).

## Principles a design is judged by

1. Resources, not actions.
2. Consistent names, parameters and response shapes on every endpoint.
3. Least surprise: HTTP used the way everyone uses it (GET never changes data; 200 never wraps an error).
4. Stateless: each request carries everything the server needs, so any server can handle it.
5. Retries are safe.
6. Anything that can grow is paginated, with a capped page size.
7. Secure by default: every endpoint authenticated unless deliberately public, and authorized for the specific resource.
8. Changes don't break existing clients: adding fields is safe; renaming or removing them needs a version.
9. Errors are actionable: the right status class plus a machine-readable code.

They earn their keep as the reason behind a decision ("an idempotency key here, so a retry can't double-book").

## Patterns

- **Pagination**: offset (`?offset=20&limit=10`) is simple and allows jumping to a page, but shifts when rows are inserted mid-scroll. Cursor (`?cursor=<last id>`, with `next_cursor` in the response) stays stable; use it for feeds and real-time data.
- **Filtering and sorting**: query parameters (`?status=paid&sort=-date`), named identically across endpoints.
- **Idempotency keys**: the client sends a unique key per logical operation; the server stores it with the first result and returns that result on a retry. Use it for payments, bookings, orders.
- **Error envelope**: one shape everywhere, `{"error": {"code": "SEAT_UNAVAILABLE", "message": "..."}}`; clients branch on the code.
- **Versioning**: in the URL (`/v1/...`) by default; in a header keeps URLs clean but is harder to see and test.

## Security

- **Authentication** establishes who the caller is; **authorization** whether they may act on this specific resource (John cancels his own bookings, not everyone's). The current user comes from the token, never from the request body.
- **JWTs** for user sessions: signed tokens carrying the user and an expiry, verifiable by any service without a lookup. A session stored in a database is the alternative.
- **API keys** for server-to-server calls and third-party developers, not for end users.
- **RBAC**: roles get permissions and users get roles; mention which roles reach which endpoints only where it matters.
- **Rate limiting** per user, per IP or per endpoint, at the gateway or in middleware; exceeding it returns 429.

---

Source: Hello Interview, [API Design](https://www.hellointerview.com/learn/courses/system-design/lesson/foundations/api-design).
