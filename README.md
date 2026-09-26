# SWE40006 Deployment Portfolio Task 4

Three small Python applications demonstrate the four sequential Docker assessment levels.

Public application: http://swe400-LoadB-BI84RULhsgD2-1629137022.us-east-1.elb.amazonaws.com/

Development, the local runtime checks, and the separate Docker-in-Docker test all ran on this Mac. The public Deployment Board runs from the versioned Docker Hub image on AWS ECS Fargate in the AWS Academy Learner Lab. An AWS Application Load Balancer gives it a stable public HTTP URL. The Raspberry Pi is not used.

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

The published starter image is `sidhaarth08/swe40006-task4-starter:1.0.0` for `linux/arm64`. The public board uses `sidhaarth08/swe40006-task4-board:1.1.0`, published for both `linux/amd64` and `linux/arm64`. The second engine for the starter pull is isolated inside a temporary `docker:29-dind` container. It needs `--privileged` to start an inner Docker daemon, so it was removed after evidence capture. The inner daemon's TCP port was not published to the host.

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

Published tags and digests, test output, screenshots, and the public grading URL are documented in the accompanying report. The public deployment has a separate lifecycle from the code repository, so check the URL before grading.

## AWS Learner Lab public deployment

`aws/deployment-board.yaml` defines one ECS Fargate task (0.25 vCPU, 0.5 GiB), a public Application Load Balancer, health checks, restricted task ingress, and seven-day log retention. The load balancer accepts HTTP on port 80 and forwards only to the task's port 8000. Its URL is public without requiring a Tailscale account or this Mac to stay awake. The AWS Academy lab supports only selected regions; this deployment uses `us-east-1` and the lab's pre-created `LabRole`.

After starting a Learner Lab session and loading its temporary CLI credentials into a local `task4-lab` profile, deploy with the default VPC and two public subnets:

```sh
aws cloudformation deploy --stack-name swe40006-task4-board \
  --template-file aws/deployment-board.yaml \
  --parameter-overrides VpcId=<default-vpc> PublicSubnetA=<public-subnet-a> PublicSubnetB=<public-subnet-b> \
  --profile task4-lab --region us-east-1
aws cloudformation describe-stacks --stack-name swe40006-task4-board \
  --profile task4-lab --region us-east-1 --query 'Stacks[0].Outputs'
```

Temporary lab credentials belong only in `~/.aws/credentials` and are never committed. The Learner Lab has a $50 budget. ECS Fargate and the load balancer can consume that budget while running; after the assessment no longer needs a live URL, delete this stack with `aws cloudformation delete-stack --stack-name swe40006-task4-board --profile task4-lab --region us-east-1` and verify deletion completed.
