#!/usr/bin/env bash
set -euo pipefail

CLOUD=${1:-both}
ENV=${2:-dev}
REPO_ROOT="$(git rev-parse --show-toplevel)"
ENV_FILE="${REPO_ROOT}/shared/environments/${ENV}.yaml"

echo "Deploying to Environment: ${ENV}"
echo "Cloud Target: ${CLOUD}"

# Helper to deploy terraform
deploy_terraform() {
    local provider=$1
    local dir="${REPO_ROOT}/infrastructure/terraform/${provider}"
    
    echo "Processing ${provider}..."
    if [ ! -d "$dir" ]; then
        echo "Directory $dir does not exist. Skipping."
        return
    fi
    
    pushd "$dir" > /dev/null
    
    # Init
    terraform init
    
    # Plan & Apply (using -var-file would require converting YAML to tfvars, 
    # for MVP we assume tfvars exist or variables are set via env vars/defaults)
    # TODO: Implement YAML -> TFVars conversion or use a tool.
    # For now, we rely on standard terraform.tfvars or defaults.
    
    terraform apply -auto-approve
    
    popd > /dev/null
}

if [[ "$CLOUD" == "gcp" || "$CLOUD" == "both" ]]; then
  deploy_terraform "gcp"
fi

if [[ "$CLOUD" == "aws" || "$CLOUD" == "both" ]]; then
  deploy_terraform "aws"
fi

echo "Deployment complete."
