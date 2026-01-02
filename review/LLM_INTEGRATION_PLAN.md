# LLM Integration Plan

## Lattice Lock Framework - Cloud LLM Integration Roadmap

This document outlines the AWS and GCP integration status, gaps, and recommended improvements for LLM provider connectivity.

## Current State

### Supported Providers

| Provider | Models | Status | Configuration |
|----------|--------|--------|---------------|
| OpenAI | 11 models | Production | `OPENAI_API_KEY` |
| Anthropic | 7 models | Production | `ANTHROPIC_API_KEY` |
| Google | 6 models | Production | `GOOGLE_API_KEY` |
| xAI | 5 models | Production | `XAI_API_KEY` |
| Ollama (Local) | 20 models | Production | `OLLAMA_HOST` |
| Azure OpenAI | 4 models | Beta | `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT` |
| AWS Bedrock | 8 models | Beta | AWS credentials |
| DIAL | 2 models | Alpha | `DIAL_API_KEY`, `DIAL_API_URL` |

### Provider Implementation Status

| Provider | File | Health Check | Chat Completion | Streaming | Error Handling |
|----------|------|--------------|-----------------|-----------|----------------|
| OpenAI | `providers/openai.py` | Yes | Yes | Yes | Yes |
| Anthropic | `providers/anthropic.py` | Yes | Yes | Yes | Yes |
| Google | `providers/google.py` | Yes | Yes | Partial | Yes |
| xAI | `providers/xai.py` | Yes | Yes | Yes | Yes |
| Local | `providers/local.py` | Yes | Yes | Yes | Yes |
| Azure | `providers/azure.py` | Yes | Yes | Yes | Partial |
| Bedrock | `providers/bedrock.py` | Partial | Yes | No | Partial |
| DIAL | `providers/dial.py` | Yes | Yes | No | Partial |

## AWS Integration Analysis

### Current Implementation

**Location:** `src/lattice_lock/orchestrator/providers/bedrock.py`

**Supported Models:**
- bedrock-claude-3-opus
- bedrock-claude-3-sonnet
- bedrock-claude-3-haiku
- bedrock-llama-3.1-405b
- bedrock-llama-3.1-70b
- bedrock-llama-3.1-8b
- bedrock-mistral-large
- bedrock-titan-express

**Configuration:**
```python
# Environment variables
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### Identified Issues

1. **Type Errors in Bedrock Client:**
   - Location: `src/lattice_lock/orchestrator/providers/bedrock.py:91, 110, 132`
   - Error: `Incompatible types in assignment (expression has type "BedrockClient", variable has type "None")`
   - Impact: Potential runtime errors

2. **Failing Tests:**
   - `tests/orchestrator/test_bedrock_implementation.py::TestBedrockClient::test_init_sets_region`
   - `tests/orchestrator/test_bedrock_implementation.py::TestBedrockClient::test_generate_calls_bedrock`
   - `tests/orchestrator/test_bedrock_implementation.py::TestBedrockClient::test_generate_handles_error`

3. **Missing Streaming Support:**
   - Bedrock supports streaming but not implemented
   - Impact: Higher latency for long responses

4. **No IAM Role Support:**
   - Only supports access key authentication
   - Impact: Cannot use EC2 instance roles or ECS task roles

### Recommended Improvements

**1. Fix Type Errors:**
```python
# src/lattice_lock/orchestrator/providers/bedrock.py
from typing import Optional
import boto3
from botocore.client import BaseClient

class BedrockClient:
    def __init__(self, region: str = "us-east-1"):
        self._client: Optional[BaseClient] = None
        self._region = region
    
    @property
    def client(self) -> BaseClient:
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self._region
            )
        return self._client
```

**2. Add IAM Role Support:**
```python
def __init__(
    self,
    region: str = "us-east-1",
    profile_name: Optional[str] = None,
    role_arn: Optional[str] = None
):
    session_kwargs = {"region_name": region}
    if profile_name:
        session_kwargs["profile_name"] = profile_name
    
    session = boto3.Session(**session_kwargs)
    
    if role_arn:
        sts = session.client("sts")
        credentials = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="lattice-lock"
        )["Credentials"]
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
    else:
        self._client = session.client("bedrock-runtime")
```

**3. Add Streaming Support:**
```python
async def stream_completion(
    self,
    prompt: str,
    model_id: str,
    **kwargs
) -> AsyncIterator[str]:
    response = self.client.invoke_model_with_response_stream(
        modelId=model_id,
        body=json.dumps({"prompt": prompt, **kwargs})
    )
    
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if "completion" in chunk:
            yield chunk["completion"]
```

## GCP Integration Analysis

### Current Implementation

**Location:** `src/database/gcp_clients.py`

**Services Used:**
- Cloud Firestore (session storage)
- BigQuery (analytics)
- Redis/Memorystore (caching)

**Missing:** Direct Vertex AI integration for LLM access

### Identified Issues

1. **Missing Dependencies:**
   - `google-cloud-firestore` not in `pyproject.toml`
   - `google-cloud-bigquery` not in `pyproject.toml`
   - `redis` not in `pyproject.toml`

2. **No Vertex AI Integration:**
   - Google models use direct API, not Vertex AI
   - Missing enterprise features (VPC-SC, CMEK)

3. **Type Errors in GCP Clients:**
   - Location: `src/database/gcp_clients.py`
   - Multiple import and type issues

### Recommended Improvements

**1. Add Vertex AI Provider:**
```python
# src/lattice_lock/orchestrator/providers/vertex.py
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

class VertexAIClient(BaseAPIClient):
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1"
    ):
        aiplatform.init(project=project_id, location=location)
        self._project_id = project_id
        self._location = location
    
    async def chat_completion(
        self,
        prompt: str,
        model_id: str = "gemini-1.5-pro",
        **kwargs
    ) -> APIResponse:
        model = aiplatform.GenerativeModel(model_id)
        response = await model.generate_content_async(prompt)
        return APIResponse(
            content=response.text,
            model=model_id,
            provider="vertex"
        )
```

**2. Add to Model Registry:**
```yaml
# src/lattice_lock/orchestrator/models.yaml
vertex-gemini-1.5-pro:
  provider: vertex
  model_id: gemini-1.5-pro
  capabilities:
    - text
    - code
    - vision
  context_window: 1000000
  pricing:
    input: 0.00125
    output: 0.00375
```

**3. Add Optional Dependencies:**
```toml
# pyproject.toml
[project.optional-dependencies]
gcp = [
    "google-cloud-aiplatform>=1.38.0",
    "google-cloud-firestore>=2.16.0",
    "google-cloud-bigquery>=3.14.0",
]
```

## Integration Roadmap

### Phase 1: Fix Existing Issues (1 week)
1. Fix Bedrock type errors
2. Fix Bedrock tests
3. Add missing GCP dependencies
4. Fix GCP client type errors

### Phase 2: AWS Enhancements (2 weeks)
5. Add IAM role support to Bedrock
6. Add streaming support to Bedrock
7. Add SageMaker endpoint support
8. Add CloudWatch metrics integration

### Phase 3: GCP Enhancements (2 weeks)
9. Add Vertex AI provider
10. Add Vertex AI models to registry
11. Add Cloud Logging integration
12. Add VPC-SC support

### Phase 4: Enterprise Features (1 month)
13. Add multi-region failover
14. Add request routing by region
15. Add cost allocation tags
16. Add compliance logging (SOC2, HIPAA)

## Configuration Examples

### AWS Bedrock with IAM Role
```bash
# .env
AWS_REGION=us-east-1
AWS_BEDROCK_ROLE_ARN=arn:aws:iam::123456789012:role/LatticeBedrockRole

# No access keys needed when using IAM roles
```

### GCP Vertex AI
```bash
# .env
GOOGLE_CLOUD_PROJECT=my-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
VERTEX_AI_LOCATION=us-central1
```

### Multi-Cloud Configuration
```yaml
# lattice.yaml
orchestrator:
  providers:
    - name: openai
      priority: 1
      regions: [us, eu]
    - name: bedrock
      priority: 2
      regions: [us]
      fallback_for: [openai]
    - name: vertex
      priority: 2
      regions: [eu]
      fallback_for: [openai]
```

## Security Considerations

### AWS
- Use IAM roles instead of access keys where possible
- Enable CloudTrail for audit logging
- Use VPC endpoints for Bedrock
- Enable encryption at rest (KMS)

### GCP
- Use Workload Identity for GKE deployments
- Enable VPC Service Controls
- Use Customer-Managed Encryption Keys (CMEK)
- Enable Cloud Audit Logs

### Cross-Cloud
- Implement request signing for all API calls
- Use secrets management (AWS Secrets Manager, GCP Secret Manager)
- Implement rate limiting per provider
- Add circuit breakers for provider failures
