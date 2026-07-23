# HTTPD package

## Scope

The `httpd` package implements the **HTTP layer** of WhakerPy.

It provides:

- a local HTTP server (based on `http.server`)
- a WSGI-compatible execution path
- a unified policy mechanism for request filtering and response post-processing

This package **does not** implement application logic.
It implements **transport, routing, and security policies**.



## Design principles

### 1. Strict separation of responsibilities

| Concern | Location |
|------|---------|
| HTTP protocol handling | `HTTPDHandler`, `BaseHTTPDServer` |
| Web application data | `WebSiteData` (outside this package) |
| HTML generation | `BaseResponseRecipe` (outside this package) |
| Security / routing policies | `HTTPDPolicy`, `Blacklist`, `SignedURL` |
| Static file access control | `FileAccessChecker`, `UnixPermissions` |
| Utilities / helpers | `HTTPDHandlerUtils`, `HTTPDStatus` |

No class mixes **data**, **business logic**, and **transport policy**.


### 2. One decision point

All request filtering and security decisions are centralized in **one class**:
`HTTPD Policy`. Neither handlers nor responses implement:

- blacklist checks
- signed URL verification
- security decisions

They delegate **once** to the policy.


### 3. Identical behavior in local HTTPD and WSGI

The same policy object is used by:

- `HTTPDHandler` (local server)
- `WSGIApplication` (uWSGI / production)

This guarantees:

- same access rules
- same error responses
- same security semantics



## Main classes and relationships

### BaseHTTPDServer

Role:

- orchestrates request handling
- stores baked pages
- owns the policy instance

Responsibilities:

- page creation (`_create_pages`)
- page baking (`page_bakery`)
- policy configuration (`configure`)
- delegation to `HTTPDPolicy`

It **does not**:

- inspect requests
- apply security rules
- know blacklist or signed URL details


### HTTPDHandler

Role:

- receive HTTP requests
- normalize paths and queries
- delegate decisions to the server policy

Flow (GET / POST):

1. extract the query string, then normalize the path
2. delegate the request to the server policy (`policy_check`)
3. serve a static file when it exists, else bake the dynamic page
4. send the response

A `GET` carries its data in the query string exactly the way a `POST`
carries it in its body: both are parsed into the same `events` dictionary
(see `parse_query_string`). Because a `GET` is a navigation and not a form
submission, query parameters the recipe does not handle (status `205`) do
not prevent the page from being served: the baked page is returned with a
`200`.

No security logic exists here.


### HTTPDPolicy

Role:

- central decision engine
- transport-level security and routing policy

Current policies implemented:

- blacklist (User-Agent and/or path)
- signed URLs (time-limited access)

Responsibilities:

- accept or reject a request
- generate standard rejection responses
- post-process outgoing HTML (`finalize_html`)

This is the **only** place where:

- blacklist logic exists
- signed URL verification exists
- HTML rewriting for signed URLs exists


### Blacklist

Role:

- store and match forbidden patterns

Characteristics:

- configuration-based
- supports file-based or dict-based configuration
- pure matching logic

It does **not**:

- decide responses
- know HTTP semantics


### SignedURL

Role:

- stateless signed URL mechanism

Characteristics:

- HMAC-based
- time-limited (TTL)
- no cookies
- no server-side state
- standard library only

It does **not**:

- know request context
- know HTML
- apply policy decisions


### HTTPDHandlerUtils

Role:

- shared helper utilities

Includes:

- response helpers
- HTML error generation
- content baking helpers
- MIME utilities
- query string parsing (`parse_query_string`, shared by GET and POST)

No policy logic here.


### FileAccessChecker / UnixPermissions

Role:

- static file access control, before any file is served

Characteristics:

- `UnixPermissions` reads the owner / group / others read bits of a file
- `FileAccessChecker` answers `read_allowed(who)` for a given file
- used by `HTTPDHandlerUtils.static_content` to refuse unreadable files

It does **not**:

- know HTTP semantics
- apply routing or blacklist rules


### HTTPDStatus

Role:

- HTTP status abstraction
- generation of consistent HTML error pages


## Request lifecycle (simplified)

HTTP request
↓
HTTPDHandler / WSGIApplication
↓
HTTPDPolicy.check(path, query, headers)
↓
├─ rejected → standard HTML error response
└─ allowed → content resolution
├─ static file
└─ dynamic page (bakery)
↓
HTTPDPolicy.finalize_html (HTML only)
↓
response sent



## Why policies are not in Responses

Responses:

- generate HTML content
- express application UI logic

They must **not**:

- know routing rules
- know security constraints
- modify URLs for transport reasons

Signed URLs, blacklist, and access rules are **transport policies**, not UI logic.


## Extensibility

New policies can be added by extending `HTTPDPolicy`, for example:

- rate limiting
- authentication
- CSP headers
- referer rules

Without modifying:

- handlers
- responses
- applications



## Summary

- `httpd` implements the **HTTP engine**
- policies are centralized, explicit, and testable
- no hidden coupling between UI and security
- same behavior in local and production environments
- no cookies, no sessions, no external dependencies

This package is the **boundary** between applications and the web.

