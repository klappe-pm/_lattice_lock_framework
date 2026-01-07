# Testing Tools, Frameworks, and CI/CD Analysis

**Status**: Analysis Complete
**Created**: 2026-01-07
**Purpose**: Define tool options, CI/CD gaps, and cloud deployment strategies

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Testing Tools Comparison](#testing-tools-comparison)
3. [CI/CD Gap Analysis](#cicd-gap-analysis)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Automated Testing Triggers](#automated-testing-triggers)
6. [Integration Recommendations](#integration-recommendations)

---

## 1. Current State Analysis

### What Exists
| Component | Tool | Status | Gap |
|-----------|------|--------|-----|
| Unit Testing | pytest | ✅ Configured | Need more markers |
| Coverage | pytest-cov | ✅ 90% target | No enforcement in CI |
| Linting | ruff | ✅ Configured | Not blocking in CI |
| Formatting | black | ✅ Configured | Not blocking in CI |
| Type Checking | mypy | ✅ Available | Not enforced |
| Pre-commit | pre-commit | ✅ Configured | Missing test hooks |
| CI Pipeline | GitHub Actions | ⚠️ Partial | No cloud deploy |
| Property Testing | hypothesis | ✅ Available | Not implemented |
| Mutation Testing | mutmut | ✅ Available | Not implemented |
| Load Testing | None | ❌ Missing | Need to add |
| Security Scanning | bandit | ⚠️ Partial | Not blocking |
| Dependency Scanning | safety | ⚠️ Partial | Not automated |

### Current CI Workflow Gaps

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CURRENT vs IDEAL PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CURRENT:   lint → test → [manual deploy]                          │
│                                                                     │
│  IDEAL:     lint → test → security → build → deploy → smoke        │
│              │      │        │         │       │        │          │
│              │      │        │         │       ▼        │          │
│              │      │        │         │    staging     │          │
│              │      │        │         │       │        │          │
│              │      │        │         │       ▼        │          │
│              │      │        │         │   production   │          │
│              ▼      ▼        ▼         ▼       ▼        ▼          │
│           BLOCKING  90%   BLOCKING   ARTIFACT GATED   BLOCKING     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Testing Tools Comparison

### Option A: Minimal Stack (Current + Enforcement)

**Tools**:
- pytest + pytest-cov (already have)
- ruff + black (already have)
- mypy (already have)
- GitHub Actions (enhance existing)

**Pros**: Minimal change, fast CI, low cost
**Cons**: No advanced testing, manual deployment
**Effort**: 2-3 days
**Cost**: Free (GitHub Actions minutes)

```yaml
# Minimal enforcement additions
quality:
  - ruff check --exit-non-zero-on-fix  # BLOCKING
  - black --check                       # BLOCKING
  - mypy src/                          # BLOCKING

tests:
  - pytest --cov-fail-under=90         # BLOCKING
```

---

### Option B: Comprehensive Stack (Recommended)

**Tools**:
| Category | Tool | Purpose | New? |
|----------|------|---------|------|
| **Testing** | pytest | Unit/integration tests | Existing |
| **Coverage** | pytest-cov + codecov | Coverage tracking | Enhance |
| **Property** | hypothesis | Property-based testing | New |
| **Mutation** | mutmut | Mutation testing | New |
| **Load** | locust | Load/performance testing | New |
| **Security** | bandit + safety + trivy | Security scanning | Enhance |
| **Docs** | pytest-markdown | Doc testing | New |
| **API** | schemathesis | API contract testing | New |
| **Linting** | ruff + black + mypy | Code quality | Existing |
| **CI/CD** | GitHub Actions + AWS/GCP | Automation | Enhance |

**Pros**: Complete coverage, catches edge cases, automated security
**Cons**: More complex, longer CI time, learning curve
**Effort**: 1-2 weeks
**Cost**: ~$50-100/month (cloud resources + CI minutes)

---

### Option C: Enterprise Stack (Maximum Quality)

**Tools** (adds to Option B):
| Category | Tool | Purpose |
|----------|------|---------|
| **Observability** | OpenTelemetry | Test telemetry |
| **Chaos** | chaos-toolkit | Chaos engineering |
| **Visual** | pytest-playwright | Visual regression |
| **Contract** | pact | Consumer-driven contracts |
| **Compliance** | checkov | IaC scanning |
| **SBOM** | syft | Software bill of materials |

**Pros**: Enterprise-grade, compliance-ready, full observability
**Cons**: High complexity, significant cost, overkill for most
**Effort**: 3-4 weeks
**Cost**: ~$200-500/month

---

## 3. CI/CD Gap Analysis

### Critical Gaps to Close

#### Gap 1: No Deployment Pipeline
**Current**: Tests run but no automated deployment
**Impact**: Manual deployment errors, inconsistent environments
**Solution**: Add build/push/deploy stages

#### Gap 2: No Staging Environment
**Current**: Direct to production (manual)
**Impact**: Untested changes in production
**Solution**: Create staging environment with automated deployment

#### Gap 3: No Security Gate
**Current**: Security scans don't block merge
**Impact**: Vulnerabilities can reach production
**Solution**: Make bandit/safety blocking on HIGH+ severity

#### Gap 4: No Rollback Automation
**Current**: Manual rollback if issues
**Impact**: Extended downtime
**Solution**: Blue-green or canary deployments with auto-rollback

#### Gap 5: No Smoke Tests Post-Deploy
**Current**: No verification after deployment
**Impact**: Silent failures in production
**Solution**: Add smoke test stage after each deployment

### Missing CI Workflows

```yaml
# MISSING: .github/workflows/deploy-staging.yml
# MISSING: .github/workflows/deploy-production.yml
# MISSING: .github/workflows/security-gate.yml
# MISSING: .github/workflows/performance-tests.yml
# MISSING: .github/workflows/smoke-tests.yml
```

---

## 4. Cloud Deployment Options

### Option A: AWS Deployment

#### Infrastructure
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   GitHub Actions                                                │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐    ┌─────────┐    ┌─────────────┐                │
│   │   ECR   │───▶│   ECS   │───▶│     ALB     │                │
│   │ (images)│    │(Fargate)│    │(load balance)│               │
│   └─────────┘    └─────────┘    └─────────────┘                │
│                       │                                         │
│                       ▼                                         │
│              ┌─────────────────┐                               │
│              │   RDS/Aurora    │                               │
│              │  (if needed)    │                               │
│              └─────────────────┘                               │
│                                                                 │
│   Supporting Services:                                          │
│   - CloudWatch (monitoring)                                     │
│   - Secrets Manager (credentials)                               │
│   - S3 (artifacts)                                             │
│   - CodePipeline (optional)                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### AWS Workflow
```yaml
# .github/workflows/deploy-aws.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-west-2
  ECR_REPOSITORY: lattice-lock
  ECS_SERVICE: lattice-lock-service
  ECS_CLUSTER: lattice-lock-cluster

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: task-definition.json
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true

      - name: Run smoke tests
        run: |
          # Wait for deployment
          sleep 30
          # Run smoke tests against deployed service
          pytest tests/smoke/ --base-url=${{ secrets.STAGING_URL }}
```

#### AWS Cost Estimate
| Service | Monthly Cost |
|---------|--------------|
| ECS Fargate (2 tasks) | ~$30 |
| ALB | ~$20 |
| ECR | ~$5 |
| CloudWatch | ~$10 |
| Secrets Manager | ~$1 |
| **Total** | **~$66/month** |

---

### Option B: GCP Deployment

#### Infrastructure
```
┌─────────────────────────────────────────────────────────────────┐
│                        GCP ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   GitHub Actions                                                │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  Artifact   │───▶│  Cloud Run  │───▶│    Load     │        │
│   │  Registry   │    │ (serverless)│    │  Balancer   │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                            │                                    │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │   Cloud SQL     │                          │
│                   │   (if needed)   │                          │
│                   └─────────────────┘                          │
│                                                                 │
│   Supporting Services:                                          │
│   - Cloud Monitoring (observability)                           │
│   - Secret Manager (credentials)                               │
│   - Cloud Storage (artifacts)                                  │
│   - Cloud Build (optional)                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### GCP Workflow
```yaml
# .github/workflows/deploy-gcp.yml
name: Deploy to GCP

on:
  push:
    branches: [main]

env:
  PROJECT_ID: lattice-lock-project
  REGION: us-central1
  SERVICE: lattice-lock

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev

      - name: Build and push
        run: |
          docker build -t ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.SERVICE }}/${{ env.SERVICE }}:${{ github.sha }} .
          docker push ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.SERVICE }}/${{ env.SERVICE }}:${{ github.sha }}

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: ${{ env.SERVICE }}
          region: ${{ env.REGION }}
          image: ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.SERVICE }}/${{ env.SERVICE }}:${{ github.sha }}

      - name: Run smoke tests
        run: |
          SERVICE_URL=$(gcloud run services describe ${{ env.SERVICE }} --region=${{ env.REGION }} --format='value(status.url)')
          pytest tests/smoke/ --base-url=$SERVICE_URL
```

#### GCP Cost Estimate
| Service | Monthly Cost |
|---------|--------------|
| Cloud Run (2 instances) | ~$20-40 |
| Artifact Registry | ~$3 |
| Cloud Monitoring | ~$10 |
| Secret Manager | ~$1 |
| **Total** | **~$34-54/month** |

---

### Cloud Comparison Matrix

| Factor | AWS | GCP | Recommendation |
|--------|-----|-----|----------------|
| **Cost** | Higher | Lower | GCP |
| **Simplicity** | Medium | High | GCP (Cloud Run) |
| **Scalability** | High | High | Tie |
| **Cold Start** | Lower (ECS) | Higher (Cloud Run) | AWS |
| **Ecosystem** | Larger | Growing | AWS |
| **CI Integration** | Excellent | Excellent | Tie |
| **Learning Curve** | Steeper | Gentler | GCP |

**Recommendation**: Start with **GCP Cloud Run** for simplicity and cost, with option to migrate to AWS ECS if more control needed.

---

## 5. Automated Testing Triggers

### Current vs Proposed Triggers

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESTING TRIGGER MATRIX                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Event                Current         Proposed                  │
│  ─────────────────────────────────────────────────────────────  │
│  git commit           pre-commit      pre-commit (enhanced)     │
│  git push             nothing         pre-push (tests)          │
│  PR opened            lint only       full test suite           │
│  PR updated           lint only       incremental tests         │
│  PR merged            nothing         deploy to staging         │
│  main push            basic CI        deploy to production      │
│  schedule (daily)     nothing         E2E + performance         │
│  manual               nothing         any workflow              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Trigger Implementation

#### 1. Pre-commit (Enhanced)
```yaml
# .pre-commit-config.yaml additions
repos:
  - repo: local
    hooks:
      # Fast checks (< 5 seconds)
      - id: ruff-fix
        name: Ruff auto-fix
        entry: ruff check --fix
        language: system
        types: [python]

      - id: black
        name: Black format
        entry: black
        language: system
        types: [python]

      # Documentation checks
      - id: doc-links
        name: Check doc links
        entry: python scripts/check_doc_links.py
        language: system
        files: \.md$
        stages: [pre-commit]
```

#### 2. Pre-push (New)
```yaml
      # Pre-push: Run tests before pushing
      - id: unit-tests
        name: Run unit tests
        entry: pytest tests/unit -x -q --tb=no
        language: system
        pass_filenames: false
        stages: [pre-push]

      - id: coverage-check
        name: Coverage check
        entry: pytest tests/unit --cov=src/lattice_lock --cov-fail-under=90 -q
        language: system
        pass_filenames: false
        stages: [pre-push]
```

#### 3. PR Triggers (GitHub Actions)
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  # Immediate feedback (< 2 min)
  quick-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: ruff check src/ tests/
      - run: black --check src/ tests/
      - run: mypy src/lattice_lock

  # Full test suite (parallel)
  tests:
    needs: quick-checks
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [unit, integration, documentation, agents]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/${{ matrix.test-type }} -v

  # Coverage gate
  coverage:
    needs: quick-checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --cov=src/lattice_lock --cov-fail-under=90 --cov-report=xml
      - uses: codecov/codecov-action@v4

  # Security scan
  security:
    needs: quick-checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install bandit safety
      - run: bandit -r src/lattice_lock -ll -x tests
      - run: safety check

  # Approver Agent review
  approver:
    needs: [tests, coverage, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: python -c "
          from lattice_lock.agents.approver import ApproverAgent
          agent = ApproverAgent()
          result = agent.review(pr_number=${{ github.event.pull_request.number }})
          print(result.to_markdown())
          exit(0 if result.approved else 1)
          "
```

#### 4. Scheduled Tests
```yaml
# .github/workflows/scheduled-tests.yml
name: Scheduled Tests

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/e2e_300/ -v --timeout=300

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/benchmarks/ --benchmark-json=benchmark.json
      - uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark.json

  mutation-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: mutmut run --paths-to-mutate=src/lattice_lock/agents/ --no-progress
        continue-on-error: true
      - run: mutmut results
```

---

## 6. Integration Recommendations

### Immediate Actions (This Week)

1. **Make linting blocking in CI**
   ```yaml
   - run: ruff check src/ --exit-non-zero-on-fix
   ```

2. **Add coverage gate**
   ```yaml
   - run: pytest --cov-fail-under=90
   ```

3. **Add pre-push hook**
   ```yaml
   stages: [pre-push]
   ```

4. **Create staging environment** (GCP Cloud Run recommended)

### Short-term Actions (Next 2 Weeks)

1. **Implement full PR workflow** (pr-checks.yml above)
2. **Add security scanning as blocking**
3. **Create deploy-staging workflow**
4. **Add smoke tests**
5. **Integrate Approver Agent into CI**

### Medium-term Actions (Next Month)

1. **Add mutation testing** (scheduled)
2. **Add performance benchmarking**
3. **Create deploy-production workflow**
4. **Set up monitoring/alerting**
5. **Implement property-based tests**

### Development Practice Changes

| Current Practice | Change To | Reason |
|-----------------|-----------|--------|
| Commit anytime | Lint/format on commit | Consistent code |
| Push anytime | Tests must pass | No broken main |
| PR without tests | Tests required | Coverage enforcement |
| Manual deploy | Auto-deploy on merge | Consistency |
| No staging | Always staging first | Safe validation |

---

## Summary: Recommended Stack

### Tools
- **Testing**: pytest + hypothesis + mutmut
- **Coverage**: pytest-cov + codecov (90% target)
- **Linting**: ruff + black + mypy (all blocking)
- **Security**: bandit + safety + trivy
- **CI/CD**: GitHub Actions
- **Cloud**: GCP Cloud Run (start), option for AWS ECS

### Triggers
- **Pre-commit**: Lint + format
- **Pre-push**: Unit tests + coverage
- **PR**: Full suite + security + Approver Agent
- **Merge to main**: Deploy staging
- **Manual approval**: Deploy production
- **Daily**: E2E + performance + mutation

### Cost
- **CI/CD**: ~$0-50/month (GitHub Actions)
- **Cloud (GCP)**: ~$35-55/month
- **Monitoring**: ~$10/month
- **Total**: ~$45-115/month
