# Microservices on EKS — CI/CD with GitHub Actions

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/microservices-eks-cicd/ci.yml?label=CI%20Tests&logo=github-actions)
![CD](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/microservices-eks-cicd/cd.yml?label=CD%20Deploy&logo=github-actions)
![AWS EKS](https://img.shields.io/badge/AWS-EKS%201.33-orange?logo=amazon-aws)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.33-blue?logo=kubernetes)
![Docker](https://img.shields.io/badge/Docker-ECR-2496ED?logo=docker)

This project extends the base microservices EKS deployment with a fully automated **CI/CD pipeline using GitHub Actions**. Every code push automatically triggers tests, builds Docker images, pushes to Amazon ECR, and deploys to EKS — with zero manual steps.

---

## What is CI/CD? (Simple Explanation)

```
Without CI/CD (manual):
  You write code → manually test → manually build Docker image
  → manually push to ECR → manually run kubectl apply → hope it works

With CI/CD (automated):
  You write code → git push → GitHub Actions does EVERYTHING automatically
```

- **CI (Continuous Integration)** — Every time you push code, tests run automatically. If tests fail, you get notified immediately and the broken code is never deployed.
- **CD (Continuous Deployment)** — When code is merged to `main` or `develop`, Docker images are built, pushed, and deployed to EKS automatically.

---

## CI/CD Pipeline Diagram

```
Developer pushes code
         │
         ▼
   ┌─────────────────────────────────────────────────┐
   │            GitHub Actions Triggers              │
   └─────────────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────────────┐
   │  CI Pipeline (ci.yml) — Runs on ALL branches   │
   │                                                 │
   │  ┌─────────────────┐   ┌────────────────────┐  │
   │  │ Test User Svc   │   │ Test Product Svc   │  │
   │  │  (Node.js Jest) │   │  (Python pytest)   │  │
   │  └────────┬────────┘   └─────────┬──────────┘  │
   │           └──────────┬───────────┘             │
   │                      ▼                         │
   │           ┌──────────────────────┐             │
   │           │  Validate K8s YAML  │             │
   │           └──────────────────────┘             │
   └─────────────────────────────────────────────────┘
         │
         │ (Only if push to main or develop)
         ▼
   ┌─────────────────────────────────────────────────┐
   │  CD Pipeline (cd.yml)                          │
   │                                                 │
   │  Step 1: Build Docker Images (3 services)      │
   │      ↓                                         │
   │  Step 2: Push to Amazon ECR (tagged with SHA)  │
   │      ↓                                         │
   │  Step 3: Connect kubectl → EKS                 │
   │      ↓                                         │
   │  Step 4: Deploy to namespace                   │
   │          main   → production namespace         │
   │          develop → staging namespace           │
   │      ↓                                         │
   │  Step 5: Wait for rolling update to complete   │
   │      ↓                                         │
   │  Step 6: Auto-rollback if deploy fails         │
   └─────────────────────────────────────────────────┘
```

---

## Branch Strategy

| Branch      | Triggers    | Deploys To           |
|-------------|-------------|----------------------|
| `feature/*` | CI only     | Nothing (tests only) |
| `develop`   | CI + CD     | `staging` namespace  |
| `main`      | CI + CD     | `production` namespace|

### Workflow

```
feature/new-login  ──┐
                     ├──► Pull Request ──► develop ──► main
feature/fix-cart   ──┘    (CI runs)       (staging)   (production)
```

---

## Project Structure

```
microservices-eks-cicd/
│
├── .github/
│   └── workflows/
│       ├── ci.yml              ← Runs tests on every push
│       └── cd.yml              ← Builds + deploys on main/develop push
│
├── k8s/
│   ├── cluster.yaml            ← EKS cluster (eksctl)
│   ├── user-service.yaml       ← Uses ${ECR_REGISTRY} and ${IMAGE_TAG}
│   ├── product-service.yaml    ← Uses ${ECR_REGISTRY} and ${IMAGE_TAG}
│   └── ingress.yaml            ← NGINX ingress routing
│
├── user-service/
│   ├── server.js               ← Must export app: module.exports = app
│   ├── server.test.js          ← NEW: Jest unit tests
│   ├── package.json            ← Includes jest + supertest devDependencies
│   └── Dockerfile
│
├── product-service/
│   ├── app.py                  ← Flask app
│   ├── test_app.py             ← NEW: pytest unit tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html
│   └── Dockerfile
│
└── README.md
```

---

## Prerequisites

Before setting up the pipeline, you need:

- The **base EKS project** already deployed (cluster running, services deployed manually once)
- A **GitHub account** with the repository created
- Your **AWS IAM credentials** (Access Key ID + Secret Access Key)
- All tools from the base project installed (**AWS CLI, kubectl, eksctl, Helm, Docker**)

---

## Setup: Step-by-Step

### Step 1 — Prepare Your K8s YAML Files

Your Kubernetes YAML files need to use **placeholders** that the CI/CD pipeline will replace at deploy time.

In `k8s/user-service.yaml`, change the image line to:
```yaml
image: ${ECR_REGISTRY}/user-service:${IMAGE_TAG}
```

In `k8s/product-service.yaml`:
```yaml
image: ${ECR_REGISTRY}/product-service:${IMAGE_TAG}
```

The CD pipeline uses `envsubst` to replace `${ECR_REGISTRY}` and `${IMAGE_TAG}` before applying.

### Step 2 — Update server.js to Export the App

The test file imports `app` from `server.js`. Add `module.exports = app` at the bottom:

```javascript
// At the bottom of user-service/server.js — add this:
if (require.main === module) {
  app.listen(3000, () => console.log('User service running on :3000'));
}
module.exports = app;   // Export for testing
```

### Step 3 — Add GitHub Secrets

Go to your GitHub repository → **Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

| Secret Name              | Value                                    |
|--------------------------|------------------------------------------|
| `AWS_ACCESS_KEY_ID`      | Your IAM access key (from the CSV file)  |
| `AWS_SECRET_ACCESS_KEY`  | Your IAM secret key (from the CSV file)  |
| `AWS_ACCOUNT_ID`         | Your 12-digit AWS account number         |

### Step 4 — Create GitHub Environments (Optional but Recommended)

Go to **Settings → Environments → New environment**

Create two environments:
- `staging` — no approval required
- `production` — add **Required reviewers** (yourself) so production needs manual approval

### Step 5 — Push the Code

```powershell
# In your project folder (PowerShell)
git add .
git commit -m "Add CI/CD pipeline with GitHub Actions"
git push origin main
```

Go to your repository → **Actions tab** — you will see the pipeline running.

---

## How the Pipeline Works (Plain English)

### ci.yml — The Test Robot

1. GitHub notices you pushed code
2. A free Ubuntu VM starts up on GitHub's servers
3. It downloads your code (`checkout`)
4. It installs Node.js and runs `npm test` on the user service
5. It installs Python and runs `pytest` on the product service
6. It validates your YAML files
7. If all tests pass → green checkmark ✅
8. If any test fails → red X ❌ and you get an email

### cd.yml — The Deploy Robot

Runs only when you push to `main` or `develop`:

1. Logs into AWS using your secrets
2. Logs Docker into ECR
3. Builds Docker images for all 3 services
4. Tags each image with the **git commit SHA** (unique identifier like `a3f7b2c`)
5. Pushes images to ECR
6. Connects `kubectl` to your EKS cluster
7. Decides which namespace to deploy to (`main` → production, `develop` → staging)
8. Replaces `${IMAGE_TAG}` in YAML with the actual commit SHA
9. Applies the YAML — Kubernetes does a rolling update (zero downtime)
10. Waits to confirm rollout succeeds
11. If something went wrong → automatically rolls back to the previous version

---

## Image Tagging Strategy

Each deployment uses the **git commit SHA** as the image tag:

```
user-service:a3f7b2c1d4e5f6g7   ← specific, permanent, traceable
user-service:latest               ← points to the most recent build
```

Why SHA tagging? If a bug is deployed, you can see exactly which commit caused it and roll back to a specific version.

---

## Monitoring Your Pipeline

### View Running Workflows
Go to your repo → **Actions** tab → click any workflow run to see live logs.

### Check Deployment Status (PowerShell)
```powershell
# Production namespace
kubectl get pods -n production
kubectl get ingress -n production

# Staging namespace
kubectl get pods -n staging
kubectl get ingress -n staging

# See rollout history (all previous versions)
kubectl rollout history deployment/user-service -n production

# Manually rollback to previous version
kubectl rollout undo deployment/user-service -n production
```

### Force a Re-deploy Without Code Changes
```powershell
# Restart pods with the latest image (useful for debugging)
kubectl rollout restart deployment/user-service -n production
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `Error: denied: User not authorized` | GitHub secrets not set | Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in repo Settings → Secrets |
| `error: no server known for "eks"` | EKS cluster not running | Start your cluster: `eksctl create cluster -f k8s/cluster.yaml` |
| `ImagePullBackOff` after deploy | ECR image push failed | Check the build-and-push job logs in the Actions tab |
| Tests fail in CI but pass locally | Different Node/Python version | Make sure your local version matches ci.yml (`node: '18'`, `python: '3.11'`) |
| `envsubst: command not found` | Ubuntu runner missing `gettext` | Add `sudo apt-get install -y gettext` before the deploy step |
| CD job skipped | Push was to a branch other than main/develop | Only pushes to `main` or `develop` trigger CD |
| `module.exports is not a function` | `server.js` doesn't export `app` | Add `module.exports = app` at the bottom of server.js |

---

## Cleanup

```powershell
# Delete all Kubernetes resources in both namespaces
kubectl delete namespace staging
kubectl delete namespace production

# Uninstall Helm releases
helm uninstall monitoring    -n monitoring
helm uninstall ingress-nginx -n ingress-nginx

# Delete ECR repositories
aws ecr delete-repository --repository-name user-service    --force
aws ecr delete-repository --repository-name product-service --force
aws ecr delete-repository --repository-name frontend        --force

# Delete the EKS cluster (stops EC2 billing)
eksctl delete cluster --name microservices-cluster --region us-east-1
```

---

## Technologies Used

| Category              | Technology                         |
|-----------------------|------------------------------------|
| CI/CD Platform        | GitHub Actions                     |
| Container Orchestration | Amazon EKS (Kubernetes 1.33)     |
| Container Registry    | Amazon ECR                         |
| Cloud Provider        | AWS (us-east-1)                    |
| Node AMI              | Amazon Linux 2023                  |
| Package Manager (K8s) | Helm v3                            |
| Ingress Controller    | NGINX Ingress Controller           |
| Test Framework (Node) | Jest + Supertest                   |
| Test Framework (Python)| pytest                            |
| Monitoring            | Prometheus + Grafana               |
| CLI Platform          | Windows PowerShell                 |

---

## Base Project

This project builds on: [microservices-eks](https://github.com/YOUR_USERNAME/microservices-eks)

---

> Learning project — covers the complete DevOps workflow from code push to automated cloud deployment.
