# CI Templates & Workflows Design (6.4.3)

**Status:** Draft
**Owner:** Gemini Antimatter
**Implementation Owner:** Devin AI

## 1. Overview
This design defines the architecture for the "Secure-by-Default" CI/CD templates provided by the Engineering Framework. These templates ensure that every Lattice Lock project starts with a production-grade pipeline including linting, testing, security auditing, and automated deployment.

## 2. Security Hardening Strategy (6.4.4)

### 2.1 Dependency Management
**Problem:** Supply chain attacks via transitive dependencies.
**Solution:**
1.  **Hash Verification:** All `requirements.txt` generation must include hash checking (`pip-compile --generate-hashes`).
2.  **Audit Step:** CI pipelines MUST run `pip-audit` or `safety` before installation.
3.  **Lock Files:** Commit `poetry.lock` or `uv.lock` (if applicable), or `requirements.lock`.

### 2.2 Permissions
- **GitHub Actions:** Use `permissions: contents: read` top-level default. Elevate only when necessary.
- **AWS/GCP:** Use OIDC (OpenID Connect) where possible to avoid long-lived keys.

## 3. Workflow Architecture

### 3.1 The "Governance Gate" Workflow
A reusable workflow that runs on every PR.
**Steps:**
1.  **Checkout**: Secure checkout.
2.  **Setup Python**: Cache dependencies.
3.  **Security Audit**: `pip-audit`.
4.  **Lint & Style**: `ruff` or `flake8`.
5.  **Lattice Validation**: `lattice-lock validate`.
    - Ensures `lattice.yaml` adheres to governance.
6.  **Sheriff Check**: `lattice-lock sheriff check`.
    - Enforces import boundaries.
7.  **Unit Tests**: `pytest`.

### 3.2 Build & Deploy Workflow
Runs on merge to main/staging.
**Steps:**
1.  **Governance Gate**: Re-run validation.
2.  **Compile**: `lattice-lock compile`.
    - Generates runtime artifacts.
3.  **Build Container**: Docker build.
4.  **Deploy**: Terraform/CloudFormation/gcloud apply.

## 4. Template Specifications

### 4.1 GitHub Actions (`templates/ci/github_actions`)
- `ci.yml`: The PR gate.
- `cd.yml`: Deployment (calls `ci.yml` as prerequisite).
- **Key Feature:** Matrix testing across Python versions [3.11, 3.12].

### 4.2 AWS CodePipeline (`templates/ci/aws`)
- `buildspec.yml`:
    - `pre_build`: Login to ECR, install deps, run `pip-audit`.
    - `build`: `lattice-lock compile`, docker build.
    - `post_build`: docker push.

### 4.3 GCP Cloud Build (`templates/ci/gcp`)
- `cloudbuild.yaml`:
    - Step 1: Install & Audit.
    - Step 2: Validate & Test.
    - Step 3: Build Image.
    - Step 4: Deploy to Cloud Run.

## 5. Implementation Notes (6.4.4)
- Update Jinja2 templates in `src/lattice_lock_cli/templates/ci/`.
- Add `pip-audit` to `setup_project` dependency list or CI environment.
- Verify existing templates against this design.
