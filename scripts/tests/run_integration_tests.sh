#!/bin/bash
# Integration Test Runner Script
# Automated test execution with multiple modes

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Model Orchestrator Integration Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse command line arguments
TEST_MODE="${1:-full}"
COVERAGE="${2:-yes}"

# Function to print section header
print_section() {
    echo -e "${YELLOW}--- $1 ---${NC}"
}

# Function to run tests with given options
run_tests() {
    local test_path="$1"
    local options="$2"
    local description="$3"

    print_section "$description"

    if [ "$COVERAGE" = "yes" ]; then
        python -m pytest "$test_path" $options \
            --cov=model-orchestrator-consolidated \
            --cov-report=term-missing \
            --cov-report=html:htmlcov
    else
        python -m pytest "$test_path" $options
    fi

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed with exit code $exit_code${NC}"
        return $exit_code
    fi
    echo ""
}

# Check dependencies
print_section "Checking dependencies"
python -c "import pytest" 2>/dev/null || {
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-asyncio pytest-cov"
    exit 1
}
python -c "import pytest_asyncio" 2>/dev/null || {
    echo -e "${YELLOW}Warning: pytest-asyncio not installed${NC}"
    echo "Install with: pip install pytest-asyncio"
}
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Run tests based on mode
case "$TEST_MODE" in
    "quick")
        print_section "Running Quick Tests (unit tests only)"
        run_tests "tests/test_orchestrator.py" "-v" "Unit Tests"
        ;;

    "integration")
        print_section "Running Integration Tests Only"
        run_tests "tests/test_integration_comprehensive.py" "-v" "Integration Tests"
        ;;

    "multi-agent")
        print_section "Running Multi-Agent Workflow Tests"
        run_tests "tests/test_integration_comprehensive.py::TestMultiAgentWorkflows" "-v" "Multi-Agent Tests"
        ;;

    "performance")
        print_section "Running Performance Tests"
        run_tests "tests/test_integration_comprehensive.py::TestPerformanceIntegration" "-v" "Performance Tests"
        ;;

    "e2e")
        print_section "Running End-to-End Tests"
        run_tests "tests/test_integration_comprehensive.py::TestEndToEndUserFlows" "-v" "E2E Tests"
        ;;

    "full")
        print_section "Running Full Test Suite"

        # Run unit tests
        run_tests "tests/test_orchestrator.py" "-v" "Unit Tests" || exit 1

        # Run integration tests
        run_tests "tests/test_integration_comprehensive.py" "-v" "Integration Tests" || exit 1

        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}All tests passed successfully!${NC}"
        echo -e "${GREEN}========================================${NC}"
        ;;

    "ci")
        print_section "Running CI Test Suite"

        # Fast mode for CI
        python -m pytest tests/ -v --tb=short -q \
            --cov=model-orchestrator-consolidated \
            --cov-report=xml:coverage.xml \
            --cov-report=term

        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✓ CI tests passed${NC}"
        else
            echo -e "${RED}✗ CI tests failed${NC}"
            exit $exit_code
        fi
        ;;

    "watch")
        print_section "Running Tests in Watch Mode"
        echo "Watching for file changes..."
        # Requires pytest-watch: pip install pytest-watch
        python -m pytest_watch tests/ -- -v
        ;;

    *)
        echo -e "${RED}Unknown test mode: $TEST_MODE${NC}"
        echo ""
        echo "Usage: $0 [mode] [coverage]"
        echo ""
        echo "Modes:"
        echo "  quick       - Unit tests only (fast)"
        echo "  integration - Integration tests only"
        echo "  multi-agent - Multi-agent workflow tests"
        echo "  performance - Performance tests"
        echo "  e2e         - End-to-end user flow tests"
        echo "  full        - All tests (default)"
        echo "  ci          - CI/CD mode with XML coverage"
        echo "  watch       - Watch mode (requires pytest-watch)"
        echo ""
        echo "Coverage:"
        echo "  yes - Enable coverage (default)"
        echo "  no  - Disable coverage"
        echo ""
        echo "Examples:"
        echo "  $0 quick no          # Quick tests without coverage"
        echo "  $0 integration yes   # Integration tests with coverage"
        echo "  $0 full              # Full suite with coverage"
        exit 1
        ;;
esac

# Print coverage report location if enabled
if [ "$COVERAGE" = "yes" ] && [ -f "htmlcov/index.html" ]; then
    echo ""
    echo -e "${BLUE}Coverage report: ${NC}file://$SCRIPT_DIR/htmlcov/index.html"
fi

# Print final summary
echo ""
echo -e "${BLUE}Test run completed at $(date)${NC}"
