# SWE40006 Deployment Portfolio Task 4

Three small Python applications demonstrate the four sequential Docker assessment levels.

Public application: https://sidhaarths-macbook-pro-m5.tailbfc8a9.ts.net/swe40006-task4/

Everything runs on this Mac. Docker Desktop is the primary Linux engine. A temporary Docker-in-Docker container starts an independent secondary engine inside Docker Desktop's Linux VM for the Hub pull/run requirement. The public board is bound to `127.0.0.1:8082` on the Mac, and Tailscale Funnel routes `/swe40006-task4` to that port. The public URL depends on the Mac being on, awake, and connected.

| Level | Application | Purpose |
|---|---|---|
| 4.1 | Official `hello-world` image | Verify Docker Engine and Hub pull |
| 4.2 | `starter-web` | Basic Flask service, published to Docker Hub and run on a second Docker environment |
| 4.3 | `deployment-board` | Separate custom web application with environment configuration and HTTP endpoints |
| 4.4 | `csv-summary` | Non-web batch CLI with bind-mounted input and persistent output |

## Run locally

Docker Engine must be running. All images are built for the current host architecture.

```sh
docker run --rm hello-world
docker build -t swe40006-starter:local starter-web
docker run --rm -d --name swe40006-starter -p 127.0.0.1:8081:8000 swe40006-starter:local
curl -fsS http://127.0.0.1:8081/health

docker build -t swe40006-board:local deployment-board
docker run -d --restart unless-stopped --name swe40006-board -p 127.0.0.1:8082:8000 \
  -e DEPLOY_ENV=portfolio -e RELEASE_VERSION=4.3.0 swe40006-board:local
curl -fsS http://127.0.0.1:8082/api/status

docker build -t swe40006-csv-summary:local csv-summary
mkdir -p output
docker run --rm --read-only --network none --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$(pwd)/csv-summary/sample",dst=/input,readonly \
  --mount type=bind,src="$(pwd)/output",dst=/output \
  swe40006-csv-summary:local --input /input/deployments.csv --output /output/summary.json
cat output/summary.json
```

The two web images use a fixed Python version, pinned Flask and Gunicorn versions, a non-root user, and a dependency layer that remains cached when only app code changes. `deployment-board` also has a Docker `HEALTHCHECK`. Neither app needs a database or secrets. The CLI has no third-party packages, no network access at runtime, and reads its sample input through a read-only mount. The `--user` override uses the host user's ID so the mounted output directory is writable without granting root access. Do not include real customer or deployment secrets in CSV inputs.

## Docker Hub and second environment

The published starter image is `sidhaarth08/swe40006-task4-starter:1.0.0`. The board image is `sidhaarth08/swe40006-task4-board:1.0.0`. Both are built for `linux/arm64`, matching Docker Desktop on this Apple Silicon Mac. The second engine is isolated inside a `docker:29-dind` container. It needs `--privileged` to start an inner Docker daemon, so it is used only for this local assessment test and can be removed after evidence capture. The inner daemon's TCP port is not published to the host.

```sh
docker run -d --privileged --name swe40006-secondary-daemon docker:29-dind
docker exec swe40006-secondary-daemon docker info
docker exec swe40006-secondary-daemon docker pull sidhaarth08/swe40006-task4-starter:1.0.0
docker exec swe40006-secondary-daemon docker run -d --name starter-from-hub \
  -p 127.0.0.1:8081:8000 sidhaarth08/swe40006-task4-starter:1.0.0
docker exec swe40006-secondary-daemon wget -qO- http://127.0.0.1:8081/health
```

The same image can be run on another compatible Docker host with:

```sh
docker pull sidhaarth08/swe40006-task4-starter:1.0.0
docker run --rm -d --name swe40006-starter -p 127.0.0.1:8081:8000 \
  sidhaarth08/swe40006-task4-starter:1.0.0
curl -fsS http://127.0.0.1:8081/health
```

Published tags and digests, test output, screenshots, and the public grading URL are documented in the submitted report. Do not assume the public deployment has the same lifecycle as the code repository; check the URL before grading.
