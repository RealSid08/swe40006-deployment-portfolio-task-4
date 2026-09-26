"""A custom deployment status board for Task 4.3."""

import os
from datetime import datetime, timezone
from html import escape

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
STARTED_AT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def status():
    return {
        "service": "deployment-board",
        "status": "ready",
        "environment": os.getenv("DEPLOY_ENV", "local"),
        "version": os.getenv("RELEASE_VERSION", "dev"),
        "started_at_utc": STARTED_AT,
    }


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/status")
def api_status():
    return jsonify(status())


@app.get("/")
def index():
    data = {key: escape(value) for key, value in status().items()}
    return render_template_string(
        """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Deployment Board | SWE40006</title><style>
:root{font-family:system-ui,-apple-system,sans-serif;color:#e8f0ed;background:#101c1d}
body{margin:0;min-height:100vh;display:grid;place-items:center}
main{width:min(700px,90vw);padding:3rem 0}small{color:#7ce7ba;letter-spacing:.15em;text-transform:uppercase}
h1{font-size:clamp(2.5rem,7vw,4.5rem);line-height:1.05;margin:.7rem 0 1.2rem}
p{color:#acbfba;line-height:1.65}.card{background:#1a2b2b;border:1px solid #36524d;border-radius:18px;padding:1.4rem 1.7rem;margin-top:2rem}
dl{display:grid;grid-template-columns:1fr 1fr;gap:1rem}dt{color:#8ca9a1;font-size:.8rem}dd{margin:.3rem 0;font-weight:650}
.badge{display:inline-block;background:#204f3b;color:#aaf0c9;padding:.45rem .8rem;border-radius:99px}
a{color:#aaf0c9}@media(max-width:500px){dl{grid-template-columns:1fr}}
</style></head><body><main><small>SWE40006 / Task 4.3</small><h1>Deployment Board</h1>
<p>A small containerized service that makes its deployment state visible. Its values come from runtime environment variables, while the image stays the same across environments.</p>
<div class="card"><span class="badge">{{ data.status }}</span><dl>
<div><dt>Environment</dt><dd>{{ data.environment }}</dd></div>
<div><dt>Release</dt><dd>{{ data.version }}</dd></div>
<div><dt>Service</dt><dd>{{ data.service }}</dd></div>
<div><dt>Started (UTC)</dt><dd>{{ data.started_at_utc }}</dd></div>
</dl></div><p><a href="api/status">View JSON status</a> · <a href="health">Health check</a></p></main></body></html>""",
        data=data,
    )
