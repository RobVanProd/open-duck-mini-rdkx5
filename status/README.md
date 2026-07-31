# Project status page

This is a read-only, evidence-oriented status page for the active ground-up
policy search. It contains no robot controls, credentials, or write endpoints.

Serve it locally from the repository root:

```bash
python3 -m http.server 8765 --directory status --bind 127.0.0.1
```

For a temporary Cloudflare quick tunnel, run `cloudflared` separately against
`http://127.0.0.1:8765`. The generated `trycloudflare.com` hostname is ephemeral
and should not be recorded as a durable project URL.

Update the page only from committed evidence. Never infer a policy pass from
training reward or elapsed training time.
