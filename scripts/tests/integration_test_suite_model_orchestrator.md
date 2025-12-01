# Benchmarks
This benchmark suite provides extensive performance testing for the Model Orchestrator using analytical models (DeepSeek R1 70B, Llama 3.1 70B) for deep performance analysis. The suite covers 8 critical performance dimensions with automated analysis and visualization capabilities.

## Quick Reference

### Installation

```bash
cd "Model Orchestrator/benchmarks"
pip install -r requirements.txt
```

### Run Benchmarks

```bash
# Quick test (10 iterations)
python benchmark_suite.py --iterations 10 --warmup 2

# Full benchmark (100 iterations)
python benchmark_suite.py

# Custom configuration
python benchmark_suite.py --iterations 200 --concurrent 20

# Using shell script
./run_benchmarks.sh
```

### Analyze Results

```bash
# Basic analysis
python benchmark_analyzer.py

# With visualizations
python benchmark_analyzer.py --visualize

# Compare against baseline
python benchmark_analyzer.py --baseline results/baseline.json --threshold 5.0
```

### Example Usage

```bash
# Run examples
python example_usage.py 1    # Quick test
python example_usage.py 2    # Comprehensive analysis
python example_usage.py all  # Run all examples
```

## Architecture

### Core Components

1. **benchmark_suite.py** (900+ lines)
   - Main benchmark execution engine
   - 8 benchmark categories
   - Configurable parameters
   - Async support for concurrent testing
   - Statistical analysis
   - JSON and Markdown reporting

2. **benchmark_analyzer.py** (600+ lines)
   - Performance regression detection
   - Bottleneck identification
   - Optimization opportunity analysis
   - Visualization generation
   - Comparative analysis

3. **example_usage.py** (400+ lines)
   - 8 usage examples
   - Integration patterns
   - Custom benchmark templates
   - CI/CD integration examples

4. **run_benchmarks.sh**
   - Automated execution script
   - Environment configuration
   - Result aggregation

## Benchmark Categories

### 1. Model Selection Speed
- **Tests**: 5 task types × complexity levels
- **Metrics**: Selection time, memory overhead, accuracy
- **Target**: <100ms p95

### 2. Memory Allocation
- **Tests**: 4 model sizes (7B, 32B, 70B, analytical)
- **Metrics**: Allocation time, peak usage, efficiency
- **Target**: <500MB for 70B models

### 3. Concurrent Request Handling
- **Tests**: 5 concurrency levels (1, 5, 10, 20, 50)
- **Metrics**: Throughput, latency, success rate
- **Target**: >100 req/sec at 10 concurrent

### 4. Cache Performance
- **Tests**: Hit vs miss scenarios
- **Metrics**: Cache hit rate, miss penalty
- **Target**: <5ms hit, <50ms miss

### 5. Startup Time
- **Tests**: Cold start performance
- **Metrics**: Initialization time, memory footprint
- **Target**: <1000ms cold start

### 6. API Response Time
- **Tests**: 3 model types × scenarios
- **Metrics**: End-to-end latency, network overhead
- **Target**: <500ms p95

### 7. Resource Utilization
- **Tests**: Sustained load (5 seconds)
- **Metrics**: CPU, memory, efficiency
- **Target**: <70% CPU average

### 8. Scalability Stress
- **Tests**: 4 load levels (10, 50, 100, 200 requests)
- **Metrics**: Breaking point, degradation, recovery
- **Target**: Handle 100+ concurrent requests

## Output Files

### Directory Structure

```
benchmark_results/
├── benchmark_results_YYYYMMDD_HHMMSS.json    # Detailed results
├── benchmark_summaries_YYYYMMDD_HHMMSS.json  # Statistical summaries
├── benchmark_report_YYYYMMDD_HHMMSS.md       # Human-readable report
├── analysis_report_YYYYMMDD_HHMMSS.md        # Analysis insights
└── visualizations/                            # Charts (if enabled)
    ├── duration_comparison.png
    ├── memory_usage.png
    ├── success_rates.png
    └── performance_distribution.png
```

### Result Format

**Detailed Results** (JSON):
```json
{
  "category_name": [
    {
      "name": "Test iteration 1",
      "category": "category_name",
      "duration_ms": 2.345,
      "memory_mb": 0.123,
      "success": true,
      "metadata": {},
      "timestamp": "2025-01-05T14:30:00"
    }
  ]
}
```

**Statistical Summary** (JSON):
```json
{
  "category_name": {
    "total_runs": 100,
    "successful_runs": 100,
    "avg_duration_ms": 2.456,
    "p50_duration_ms": 2.345,
    "p95_duration_ms": 3.789,
    "p99_duration_ms": 4.123,
    "success_rate": 100.0
  }
}
```

## Performance Targets

### Response Time Targets

| Operation | Average | P95 | P99 |
|-----------|---------|-----|-----|
| Model selection | <50ms | <100ms | <200ms |
| Cache hit | <5ms | <10ms | <20ms |
| Cache miss | <30ms | <50ms | <100ms |
| API response | <200ms | <500ms | <1000ms |
| Concurrent request | <100ms | <200ms | <500ms |

### Resource Targets

| Resource | Target | Maximum |
|----------|--------|---------|
| RAM efficiency | <80% | <90% |
| CPU utilization | <60% | <70% |
| Success rate | >99% | - |
| Throughput | >100 req/s | - |

### Scalability Targets

| Load Level | Concurrent | Target Latency |
|------------|-----------|----------------|
| Light | 10 | <100ms |
| Medium | 50 | <200ms |
| Heavy | 100 | <500ms |
| Extreme | 200+ | Graceful degradation |

## Analysis Capabilities

### 1. Performance Regression Detection

Compares current results against baseline:
- Identifies metric degradations
- Classifies severity (critical, high, medium, low)
- Provides specific regression percentages
- Highlights concerning trends

**Example Output**:
```
CRITICAL: model_selection_code_generation - Average Duration
  Baseline: 2.456ms
  Current: 5.123ms
  Regression: +108.6%
```

### 2. Bottleneck Identification

Analyzes performance bottlenecks:
- Detects operations >100ms average
- Analyzes P95/P99 outliers
- Classifies impact
- Provides targeted recommendations

**Example Output**:
```
HIGH: concurrent_20_reasoning
  Average: 234.56ms
  P95: 456.78ms
  Recommendation: Optimize async handling and reduce lock contention
```

### 3. Optimization Opportunities

Identifies improvement areas:
- Low success rates
- High memory usage
- Cache optimization opportunities
- Prioritizes by impact and effort

**Example Output**:
```
HIGH priority: cache_performance
  Opportunity: Implement intelligent caching strategy
  Potential: Reduce cache miss penalty by 50-70%
  Effort: low
```

### 4. Visualization

Generates charts (requires matplotlib):
- Duration comparison (average vs P95)
- Memory usage (average vs peak)
- Success rate distribution
- Performance distribution plots

## Best Practices

### Before Running Benchmarks

1. **System Preparation**
   - Close unnecessary applications
   - Disable background processes
   - Ensure stable network
   - Verify sufficient disk space

2. **Configuration**
   - Use ≥100 iterations for statistical significance
   - Enable 10+ warmup iterations
   - Configure appropriate concurrency
   - Enable memory tracking for detailed analysis

3. **Baseline Establishment**
   - Run baseline before changes
   - Save baseline results
   - Document system configuration

### During Benchmarking

1. **Monitoring**
   - Watch system resources
   - Check for thermal throttling
   - Monitor disk I/O
   - Verify network stability

2. **Isolation**
   - Prevent interference
   - Maintain consistent environment
   - Avoid system updates

### After Benchmarking

1. **Analysis**
   - Focus on percentiles (P95, P99)
   - Compare against baseline
   - Identify patterns
   - Validate findings

2. **Action Items**
   - Address critical regressions
   - Optimize identified bottlenecks
   - Implement recommendations
   - Track improvements

## Integration Patterns

### CI/CD Pipeline

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmarks

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd "Model Orchestrator/benchmarks"
          pip install -r requirements.txt

      - name: Run benchmarks
        run: |
          cd "Model Orchestrator/benchmarks"
          python benchmark_suite.py --iterations 50 --output-dir ci_results

      - name: Analyze results
        run: |
          cd "Model Orchestrator/benchmarks"
          python benchmark_analyzer.py --results-dir ci_results --threshold 5.0

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: Model Orchestrator/benchmarks/ci_results/
```

### Performance Gates

```python
# check_performance.py
from benchmark_analyzer import BenchmarkAnalyzer
import sys

analyzer = BenchmarkAnalyzer("ci_results")
analyzer.load_latest_results()
analyzer.load_baseline_results("baseline/baseline.json")
analyzer.analyze_performance_regressions(threshold=5.0)

# Fail if critical regressions
critical = [r for r in analyzer.regressions if r.severity == "critical"]
if critical:
    print(f"FAIL: {len(critical)} critical regressions")
    sys.exit(1)

print("PASS: No critical regressions")
```

## Advanced Usage

### Custom Benchmarks

Extend the suite with custom tests:

```python
from benchmark_suite import BenchmarkSuite, BenchmarkResult

class CustomSuite(BenchmarkSuite):
    def benchmark_custom_feature(self):
        results = []
        for i in range(self.config.iterations):
            # Your benchmark logic
            result = BenchmarkResult(
                name=f"Custom test {i}",
                category="custom",
                duration_ms=duration,
                memory_mb=memory,
                success=True
            )
            results.append(result)

        self.results["custom"] = results
```

### Parallel Execution

Run multiple configurations in parallel:

```python
from concurrent.futures import ProcessPoolExecutor

configs = [
    BenchmarkConfig(output_dir=Path(f"run_{i}"))
    for i in range(4)
]

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(BenchmarkSuite(c).run_all_benchmarks)
        for c in configs
    ]
    [f.result() for f in futures]
```

### Historical Trend Analysis

Track performance over time:

```python
import json
import pandas as pd
from pathlib import Path

# Load all results
data = []
for file in sorted(Path("results").glob("benchmark_summaries_*.json")):
    with open(file) as f:
        timestamp = file.stem.split('_')[-2:]
        data.append({'timestamp': timestamp, 'data': json.load(f)})

# Analyze trends
df = pd.DataFrame(data)
# ... trend analysis
```

## Troubleshooting

### Common Issues

**High Memory Usage**
- Reduce concurrent requests
- Use smaller model sizes
- Increase system RAM
- Enable swap space

**Inconsistent Results**
- Increase warmup iterations
- Increase total iterations
- Isolate system resources
- Check background processes

**Slow Execution**
- Reduce iterations initially
- Disable memory tracking
- Skip heavy stress tests
- Use faster models

**Import Errors**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.8+
```

**Permission Errors**
```bash
# Make scripts executable
chmod +x run_benchmarks.sh
```

## Performance Optimization Guide

Based on benchmark results:

### Model Selection
- **Issue**: Slow selection (>100ms)
- **Solutions**:
  - Implement selection caching
  - Pre-compute common patterns
  - Optimize decision tree
  - Use lookup tables

### Memory Management
- **Issue**: High memory usage (>1GB)
- **Solutions**:
  - Implement model pooling
  - Use lazy loading
  - Optimize buffer sizes
  - Implement aggressive GC

### Concurrency
- **Issue**: Poor scalability
- **Solutions**:
  - Tune worker pool size
  - Reduce lock contention
  - Optimize async patterns
  - Implement request batching

### Caching
- **Issue**: Low hit rate (<80%)
- **Solutions**:
  - Increase cache size
  - Implement smart eviction
  - Pre-warm common models
  - Use predictive loading

### API Performance
- **Issue**: High latency (>500ms)
- **Solutions**:
  - Batch requests
  - Implement request coalescing
  - Optimize serialization
  - Use connection pooling

## Metrics Reference

### Duration Metrics

- **Average**: Mean execution time
- **P50** (median): 50th percentile
- **P95**: 95th percentile (target SLO)
- **P99**: 99th percentile (extreme cases)
- **Min/Max**: Bounds

### Memory Metrics

- **Average**: Mean memory usage
- **Peak**: Maximum observed
- **Allocated**: Total allocated
- **Efficiency**: Usage per operation

### Success Metrics

- **Success rate**: % successful operations
- **Error rate**: % failed operations
- **Retry rate**: % requiring retry

### Throughput Metrics

- **Requests/second**: Processing rate
- **Latency**: Time per request
- **Concurrency**: Parallel capacity

## Version History

- **1.0.0** (2025-01-05): Initial release
  - 8 benchmark categories
  - Comprehensive analysis
  - Visualization support
  - CI/CD integration
  - Example usage patterns

## Future Enhancements

Planned improvements:

1. **Additional Benchmarks**
   - Model loading time
   - Context switching overhead
   - Provider failover latency
   - Token counting performance

2. **Advanced Analysis**
   - Machine learning prediction
   - Anomaly detection
   - Comparative analysis
   - Trend forecasting

3. **Visualization**
   - Interactive dashboards
   - Real-time monitoring
   - Historical trends
   - Comparative charts

4. **Integration**
   - Prometheus metrics
   - Grafana dashboards
   - Cloud provider integration
   - Automated reporting

## References

- Main documentation: `README.md`
- Example usage: `example_usage.py`
- Execution script: `run_benchmarks.sh`
- Analysis tool: `benchmark_analyzer.py`

## Support

For issues or questions:

1. Check this summary
2. Review README.md
3. Examine example_usage.py
4. Check generated reports

## License

Part of the Power Prompts Model Orchestrator system.



# Integration Test Suite - Model Orchestrator
## Overview

This test suite provides complete integration testing coverage for:
1. Multi-agent workflow orchestration
2. Model selection and API integration
3. External service mocking and testing
4. Error handling and recovery
5. Performance characteristics
6. End-to-end user workflows

## Test Files

`test_integration_comprehensive.py`
Primary integration test suite with 8 major test categories and 35+ test cases.

**Test Categories:**
1. **Multi-Agent Workflows** - Tests parallel execution, sequential coordination, failure recovery, and consensus selection
2. **Model Orchestrator Integration** - Tests complete request lifecycle, cost optimization, and fallback chains
3. **API Endpoint Mocking** - Tests rate limits, timeouts, response validation, and concurrent calls
4. **Database/File System Integration** - Tests persistence of cost tracking, performance history, and model registry
5. **External Service Mocking** - Tests mocking of Ollama, cloud APIs, and model guides
6. **Error Scenarios** - Tests invalid inputs, network errors, and concurrent failure isolation
7. **Performance Integration** - Tests selection performance, concurrent throughput, and memory efficiency
8. **End-to-End User Flows** - Tests code generation, debugging, multi-turn conversations, and consensus workflows

## Running Tests
### Run All Integration Tests

```bash
cd "/Users/kevinlappe/Obsidian/Power Prompts/Model Orchestrator"
python -m pytest tests/test_integration_comprehensive.py -v
```

### Run Specific Test Category
```bash
# Multi-agent workflow tests
python -m pytest tests/test_integration_comprehensive.py::TestMultiAgentWorkflows -v

# Performance tests
python -m pytest tests/test_integration_comprehensive.py::TestPerformanceIntegration -v

# End-to-end flows
python -m pytest tests/test_integration_comprehensive.py::TestEndToEndUserFlows -v
```

### Run with Coverage
```bash
python -m pytest tests/test_integration_comprehensive.py --cov=model-orchestrator-consolidated --cov-report=html
```

### Run Async Tests
```bash
# Install async support if needed
pip install pytest-asyncio

# Run with async mode
python -m pytest tests/test_integration_comprehensive.py --asyncio-mode=auto -v
```


## Test Fixtures

### `orchestrator_with_mocks`
Fully mocked orchestrator with injectable dependencies. Use for:
- Isolated component testing
- API failure simulation
- Performance testing without network overhead

```python
async def test_example(orchestrator_with_mocks):
    response = await orchestrator_with_mocks.call_model(
        model_id="codellama:34b",
        messages=[{"role": "user", "content": "Test"}]
    )
    assert response.content
```

### `mock_multi_agent_context`

Simulates multi-agent execution environment. Use for:
- Agent coordination testing
- Parallel execution workflows
- Agent failure scenarios

```python
def test_example(mock_multi_agent_context):
    agents = mock_multi_agent_context["agents"]
    assert len(agents) == 3
    assert agents[0]["model"] == "codellama:34b"
```

### `temp_dir`

Temporary directory for file system tests. Automatically cleaned up.

```python
def test_example(temp_dir):
    file_path = Path(temp_dir) / "test.json"
    with open(file_path, 'w') as f:
        json.dump({"test": "data"}, f)
    assert file_path.exists()
```

## Test Patterns

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_operation(orchestrator_with_mocks):
    response = await orchestrator_with_mocks.call_model(
        model_id="codellama:34b",
        messages=[{"role": "user", "content": "Test"}]
    )
    assert isinstance(response, APIResponse)
```

### Mock API Response Pattern
```python
def test_with_mock_response(orchestrator_with_mocks, mock_api_responses):
    client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]
    client.chat_completion.return_value = mock_api_responses["success"]

    # Test code here
```

### Concurrent Execution Pattern
```python
@pytest.mark.asyncio
async def test_concurrent(orchestrator_with_mocks):
    tasks = [
        orchestrator_with_mocks.call_model(...)
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 10
```

### Error Simulation Pattern
```python
@pytest.mark.asyncio
async def test_error_handling(orchestrator_with_mocks):
    client = orchestrator_with_mocks.api_clients[ModelProvider.LOCAL]
    client.chat_completion.side_effect = Exception("Test error")

    with pytest.raises(Exception):
        await orchestrator_with_mocks.call_model(...)
```



## CICD
### GitHub Actions Workflow
```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run integration tests
        run: |
          cd "Model Orchestrator"
          python -m pytest tests/test_integration_comprehensive.py -v --cov
```

### Pre-commit Hook
```bash
#!/bin/bash
# Run integration tests before commit
cd "Model Orchestrator"
python -m pytest tests/test_integration_comprehensive.py --tb=short -q
if [ $? -ne 0 ]; then
    echo "Integration tests failed. Commit aborted."
    exit 1
fi
```

[[Developer Docs/Troubleshooting Guide]]


# Model Orchestrator Benchmark Suite

Comprehensive performance benchmarking suite using analytical models (DeepSeek R1 70B, Llama 3.1 70B) for deep performance analysis.

## Overview

This benchmark suite provides extensive performance testing across 8 critical dimensions:

1. **Model Selection Speed** - Algorithm performance and decision-making efficiency
2. **Memory Allocation** - Memory usage patterns across different model sizes
3. **Concurrent Request Handling** - Parallel processing capabilities
4. **Cache Performance** - Caching effectiveness and hit/miss ratios
5. **Startup Time Optimization** - Initialization and warmup performance
6. **API Response Time** - End-to-end latency measurements
7. **Resource Utilization** - CPU and memory usage under load
8. **Scalability Stress Tests** - System behavior under extreme load

## Quick Start

### Basic Usage

Run the complete benchmark suite with default settings:

```bash
cd "Model Orchestrator/benchmarks"
python benchmark_suite.py
```

### Custom Configuration

Run with custom parameters:

```bash
python benchmark_suite.py \
  --iterations 200 \
  --warmup 20 \
  --concurrent 20 \
  --output-dir custom_results
```

### Analyze Results

Analyze the most recent benchmark results:

```bash
python benchmark_analyzer.py
```

Generate visualizations:

```bash
python benchmark_analyzer.py --visualize
```

Compare against specific baseline:

```bash
python benchmark_analyzer.py \
  --baseline benchmark_results/benchmark_summaries_20250105_143000.json \
  --threshold 5.0
```

## Benchmark Categories

### 1. Model Selection Speed

Tests the performance of the model selection algorithm across different task types and complexity levels.

**Key Metrics**:
- Average selection time
- P95 and P99 latencies
- Memory overhead
- Selection accuracy

**Test Cases**:
- Simple code generation (low complexity)
- Complex reasoning (high complexity)
- System design (high complexity)
- Quick Q&A (low complexity)
- Data analysis (medium complexity)

### 2. Memory Allocation

Measures memory usage patterns for different model sizes and allocation strategies.

**Key Metrics**:
- Average memory allocation
- Peak memory usage
- Allocation time
- Memory efficiency

**Test Models**:
- Small models (7B parameters)
- Medium models (32B parameters)
- Large models (70B parameters)
- Analytical models (DeepSeek R1, Llama 3.1)

### 3. Concurrent Request Handling

Tests the system's ability to handle multiple simultaneous requests.

**Key Metrics**:
- Throughput (requests/second)
- Average latency per request
- Success rate under load
- Resource contention

**Concurrency Levels**:
- 1, 5, 10, 20, 50 concurrent requests

### 4. Cache Performance

Evaluates caching effectiveness and optimization opportunities.

**Key Metrics**:
- Cache hit rate
- Cache miss penalty
- Average response time
- Memory overhead

**Test Scenarios**:
- Cold cache (first access)
- Warm cache (repeated access)
- Cache eviction patterns

### 5. Startup Time Optimization

Measures initialization and warmup performance.

**Key Metrics**:
- Initialization time
- Warmup duration
- Memory footprint at startup
- Time to first request

### 6. API Response Time

Benchmarks end-to-end API response times across different model types.

**Key Metrics**:
- Average response time
- P95 and P99 latencies
- Network overhead
- Model-specific performance

**Test Scenarios**:
- Fast local models
- Medium complexity models
- High reasoning models

### 7. Resource Utilization

Monitors CPU and memory usage under sustained load.

**Key Metrics**:
- Average CPU utilization
- Peak CPU usage
- Average memory usage
- Peak memory usage
- Resource efficiency

### 8. Scalability Stress Tests

Tests system behavior under extreme load conditions.

**Key Metrics**:
- Maximum throughput
- Breaking point
- Graceful degradation
- Recovery time

**Stress Levels**:
- Light load (10 requests)
- Medium load (50 requests)
- Heavy load (100 requests)
- Extreme load (200 requests)

## Configuration Options

### BenchmarkConfig Parameters

```python
@dataclass
class BenchmarkConfig:
    iterations: int = 100              # Iterations per test
    warmup_iterations: int = 10        # Warmup runs
    concurrent_requests: int = 10      # Max concurrent requests
    enable_profiling: bool = True      # Enable detailed profiling
    enable_memory_tracking: bool = True # Track memory usage
    output_dir: Path = Path("benchmark_results")
    use_analytical_models: bool = True # Use DeepSeek/Llama for analysis
    analytical_models: List[str] = ["deepseek-r1-70b", "llama-3.1-70b"]
```

### Command Line Options

```
--iterations N          Number of iterations per benchmark (default: 100)
--warmup N             Number of warmup iterations (default: 10)
--concurrent N         Number of concurrent requests (default: 10)
--output-dir PATH      Output directory for results
--no-profiling         Disable profiling
--no-memory-tracking   Disable memory tracking
```

## Output Files

The benchmark suite generates three types of output files:

### 1. Detailed Results (JSON)

**File**: `benchmark_results_YYYYMMDD_HHMMSS.json`

Contains individual test results with full metadata:

```json
{
  "model_selection_code_generation_low": [
    {
      "name": "Simple code generation (iteration 1)",
      "category": "model_selection_speed",
      "duration_ms": 2.345,
      "memory_mb": 0.123,
      "success": true,
      "metadata": {
        "task_type": "code_generation",
        "complexity": "low",
        "selected_model": "qwen-2.5-7b-instruct"
      },
      "timestamp": "2025-01-05T14:30:00"
    }
  ]
}
```

### 2. Statistical Summaries (JSON)

**File**: `benchmark_summaries_YYYYMMDD_HHMMSS.json`

Contains aggregated statistics for each benchmark category:

```json
{
  "model_selection_code_generation_low": {
    "category": "model_selection_code_generation_low",
    "total_runs": 100,
    "successful_runs": 100,
    "failed_runs": 0,
    "avg_duration_ms": 2.456,
    "p50_duration_ms": 2.345,
    "p95_duration_ms": 3.789,
    "p99_duration_ms": 4.123,
    "avg_memory_mb": 0.145,
    "peak_memory_mb": 0.234,
    "success_rate": 100.0
  }
}
```

### 3. Human-Readable Report (Markdown)

**File**: `benchmark_report_YYYYMMDD_HHMMSS.md`

Formatted report with:
- Configuration details
- Summary statistics per category
- Performance recommendations
- Identified issues and optimizations

## Analysis Tools

### Benchmark Analyzer

The analyzer provides:

1. **Performance Regression Detection**
   - Compares current results against baseline
   - Identifies degradations across all metrics
   - Classifies severity (critical, high, medium, low)

2. **Bottleneck Identification**
   - Detects slow operations
   - Analyzes P95/P99 latencies
   - Provides targeted recommendations

3. **Optimization Opportunities**
   - Identifies improvement areas
   - Estimates potential gains
   - Prioritizes by impact and effort

4. **Visualization Generation**
   - Duration comparison charts
   - Memory usage charts
   - Success rate charts
   - Performance distribution plots

### Analysis Output

**File**: `analysis_report_YYYYMMDD_HHMMSS.md`

Contains:
- Performance regressions with severity classification
- Identified bottlenecks with recommendations
- Optimization opportunities with priority ranking
- Visual charts (if matplotlib available)

## Performance Targets

### Response Time Targets

- Model selection: <100ms (p95)
- Cache hit: <5ms average
- Cache miss: <50ms average
- Concurrent request: <200ms per request
- API response: <500ms (p95)

### Resource Utilization Targets

- RAM efficiency: <90% peak usage
- CPU utilization: <70% average
- Success rate: >99%
- Throughput: >100 requests/second

### Scalability Targets

- Handle 100 concurrent requests
- Maintain <500ms latency under load
- Graceful degradation beyond capacity
- Quick recovery (<5s) from overload

## Best Practices

### Running Benchmarks

1. **Isolate System Resources**
   - Close unnecessary applications
   - Disable background processes
   - Ensure stable network connection

2. **Use Sufficient Iterations**
   - Minimum 100 iterations for statistical significance
   - Use 10+ warmup iterations
   - Consider variance in results

3. **Monitor System State**
   - Check available RAM before starting
   - Monitor temperature/throttling
   - Verify disk space for results

4. **Baseline Comparison**
   - Establish baseline before changes
   - Run benchmarks consistently
   - Track historical trends

### Analyzing Results

1. **Focus on Percentiles**
   - P95 and P99 more important than average
   - Identify outliers and anomalies
   - Understand distribution shape

2. **Compare Apples to Apples**
   - Same hardware configuration
   - Same software versions
   - Same test parameters

3. **Look for Patterns**
   - Consistent degradations
   - Correlated metrics
   - Systematic issues

4. **Validate Findings**
   - Re-run suspicious results
   - Test hypotheses
   - Verify improvements

## Integration with CI/CD

### Automated Benchmarking

Add to your CI pipeline:

```yaml
benchmark:
  stage: test
  script:
    - python benchmarks/benchmark_suite.py --iterations 50 --output-dir ci_results
    - python benchmarks/benchmark_analyzer.py --results-dir ci_results --threshold 5.0
  artifacts:
    paths:
      - ci_results/
    expire_in: 30 days
  only:
    - main
    - develop
```

### Performance Gates

Fail builds on regressions:

```python
# In your CI script
analyzer = BenchmarkAnalyzer("ci_results")
analyzer.load_latest_results()
analyzer.load_baseline_results(baseline_file)
analyzer.analyze_performance_regressions(threshold=5.0)

if analyzer.regressions:
    critical_regressions = [r for r in analyzer.regressions if r.severity == "critical"]
    if critical_regressions:
        print(f"FAIL: {len(critical_regressions)} critical regressions detected")
        sys.exit(1)
```

## Troubleshooting

### Common Issues

#### High Memory Usage

**Symptom**: Benchmarks fail with OOM errors

**Solutions**:
- Reduce concurrent requests
- Use smaller model sizes
- Increase system RAM
- Enable swap space

#### Inconsistent Results

**Symptom**: High variance in measurements

**Solutions**:
- Increase warmup iterations
- Increase total iterations
- Isolate system resources
- Check for background processes

#### Slow Execution

**Symptom**: Benchmarks take too long

**Solutions**:
- Reduce iterations for initial testing
- Disable memory tracking
- Skip heavy stress tests
- Use faster models for testing

### Getting Help

For issues or questions:

1. Check this README
2. Review example output files
3. Examine benchmark logs
4. Consult main documentation

## Advanced Usage

### Custom Benchmark Categories

Add custom benchmarks by extending `BenchmarkSuite`:

```python
class CustomBenchmarkSuite(BenchmarkSuite):
    def benchmark_custom_feature(self):
        """Custom benchmark implementation"""
        results = []

        for i in range(self.config.iterations):
            # Your benchmark logic here
            result = BenchmarkResult(
                name=f"Custom test {i}",
                category="custom_feature",
                duration_ms=duration,
                memory_mb=memory,
                success=True
            )
            results.append(result)

        self.results["custom_feature"] = results
```

### Parallel Execution

Run multiple benchmark suites in parallel:

```python
from concurrent.futures import ProcessPoolExecutor

configs = [
    BenchmarkConfig(iterations=100, output_dir=Path(f"run_{i}"))
    for i in range(4)
]

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(BenchmarkSuite(config).run_all_benchmarks)
        for config in configs
    ]

    for future in futures:
        future.result()
```

### Historical Trend Analysis

Track performance over time:

```python
import pandas as pd

# Load all historical results
results = []
for summary_file in sorted(Path("benchmark_results").glob("benchmark_summaries_*.json")):
    with open(summary_file) as f:
        data = json.load(f)
        results.append({
            'timestamp': summary_file.stem.split('_')[-2:],
            'data': data
        })

# Convert to DataFrame and analyze trends
df = pd.DataFrame(results)
# ... trend analysis logic
```

## Performance Optimization Tips

Based on benchmark results, consider these optimizations:

1. **Model Selection**
   - Cache frequent selections
   - Pre-load common models
   - Optimize decision tree

2. **Memory Management**
   - Implement model pooling
   - Use lazy loading
   - Optimize buffer sizes

3. **Concurrency**
   - Tune worker pool size
   - Reduce lock contention
   - Optimize async patterns

4. **Caching**
   - Increase cache size
   - Implement intelligent eviction
   - Pre-warm frequently accessed models

5. **API Optimization**
   - Batch requests when possible
   - Implement request coalescing
   - Optimize serialization

## Version History

- **1.0.0** (2025-01-05): Initial release
  - 8 benchmark categories
  - Comprehensive analysis tools
  - Visualization support
  - CI/CD integration

## License

Part of the Power Prompts Model Orchestrator system.

## Contributing

Contributions welcome! Areas for enhancement:

- Additional benchmark categories
- More visualization options
- Advanced statistical analysis
- Machine learning-based prediction
- Comparative analysis across versions


