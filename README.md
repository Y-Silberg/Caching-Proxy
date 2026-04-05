# 🔀 Simple Caching HTTP Proxy

A lightweight, in-memory caching HTTP proxy written in Python. It sits between your client and an origin server, forwarding requests and caching GET responses to reduce redundant network calls.

---

## Features

- **In-memory caching** — GET responses are cached by URL path for the duration of the process
- **Cache hit/miss logging** — logs `X-Cache: HIT` or `X-Cache: MISS` for every request
- **Configurable** — port, origin host, and cache clearing are all controlled via CLI flags
- **Persistent connections** — handles multiple sequential requests per connection

---

## Requirements

- Python 3.6+

---

## Usage

```bash
python3 proxy.py [--port PORT] [--origin ORIGIN] [--clear-cache]
```

### Arguments

| Argument        | Type    | Default          | Description                          |
|-----------------|---------|------------------|--------------------------------------|
| `--port`        | `int`   | `3000`           | Local port the proxy listens on      |
| `--origin`      | `str`   | `vanilla.co.za`  | The origin server to proxy requests to |
| `--clear-cache` | flag    | `False`          | Clear the in-memory cache and exit   |

### Examples

**Start the proxy on the default port:**
```bash
python proxy.py
```

**Proxy to a custom origin on a custom port:**
```bash
python proxy.py --port 8080 --origin example.com
```

**Clear the cache and exit:**
```bash
python proxy.py --clear-cache
```

---

## How It Works

```
Client → proxy.py (your machine) → Origin Server (port 80)
```

1. The proxy binds to `0.0.0.0` on the specified port and listens for incoming TCP connections.
2. For each request, it extracts the HTTP method and path from the first line of the request.
3. **If the method is GET** and the path is already in the cache → the cached response is returned immediately (`X-Cache: HIT`).
4. **Otherwise**, the request is forwarded to the origin server with the `Host` header rewritten, and the response is stored in cache (`X-Cache: MISS`).
5. Non-GET requests (POST, PUT, etc.) are forwarded as-is and are never cached.

---

## Caching Behaviour

- Only `GET` requests are cached.
- The cache key is the **URL path** (e.g. `/index.html`, `/api/data`).
- The cache is **in-memory only** — it resets when the process restarts.
- Use `--clear-cache` to explicitly wipe the cache at startup (useful in scripts).

---

## Limitations

- Forwards requests over **HTTP only** (port 80) — HTTPS is not supported.
- No cache expiry or TTL — entries persist for the lifetime of the process.
- Designed for single-origin proxying; one origin per instance.