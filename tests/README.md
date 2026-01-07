# Testing Framework

## Overview

This directory contains tests for validating the personal operating system components.

## Test Structure

```
tests/
├── README.md                    # This file
├── excel_io_validation.md      # Excel I/O validation procedures
├── job_discovery_tests.py      # Job discovery automation tests
├── resume_tailoring_tests.py   # Resume tailoring tests
└── outreach_flow_tests.py      # Outreach generation tests
```

## Testing Philosophy

### Goals
1. **Validate Functionality**: Ensure scripts work as expected
2. **Prevent Regressions**: Catch breaking changes early
3. **Document Behavior**: Tests serve as documentation
4. **Enable Confidence**: Make changes with confidence

### Approach
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Manual Validation**: Human review of outputs

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-cov
```

### Run All Tests
```bash
cd tests
pytest -v
```

### Run Specific Test File
```bash
pytest job_discovery_tests.py -v
```

### Run with Coverage
```bash
pytest --cov=../automation --cov-report=html
```

### Run Specific Test
```bash
pytest job_discovery_tests.py::TestJobScraper::test_score_calculation -v
```

## Test Categories

### 1. Job Discovery Tests
**File**: `job_discovery_tests.py`

**Tests**:
- Job scraping functionality
- Filtering logic
- Scoring calculation
- Data export format
- Error handling

### 2. Resume Tailoring Tests
**File**: `resume_tailoring_tests.py`

**Tests**:
- Resume parsing
- Keyword extraction
- Content tailoring
- Format preservation
- Output validation

### 3. Outreach Flow Tests
**File**: `outreach_flow_tests.py`

**Tests**:
- Message generation
- Personalization
- Template rendering
- Quality checks
- Length validation

### 4. Excel I/O Tests
**File**: `excel_io_validation.md`

**Procedures**:
- Read operations
- Write operations
- Data integrity
- Format preservation
- Error handling

## Writing New Tests

### Test Template
```python
import pytest
from automation.module import function_to_test

class TestFeatureName:
    """Test suite for feature."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = {...}
    
    def test_basic_functionality(self):
        """Test basic functionality works."""
        result = function_to_test(self.test_data)
        assert result is not None
        assert result['status'] == 'success'
    
    def test_edge_case(self):
        """Test edge case handling."""
        result = function_to_test(edge_case_data)
        assert result is not None
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function_to_test(invalid_data)
```

### Best Practices
1. **One test, one assertion**: Test one thing at a time
2. **Descriptive names**: Test name should describe what it tests
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Independent tests**: Tests shouldn't depend on each other
5. **Use fixtures**: Share setup code via fixtures
6. **Mock external services**: Don't hit real APIs in tests
7. **Test edge cases**: Include boundary conditions
8. **Document intent**: Add docstrings explaining why

## Test Data

### Test Fixtures
Store test data in `tests/fixtures/`:
- Sample job postings
- Sample resumes
- Sample configuration
- Expected outputs

### Generating Test Data
```python
@pytest.fixture
def sample_job_posting():
    """Provide sample job posting for tests."""
    return {
        'title': 'Software Engineer',
        'company': 'Test Corp',
        'description': '...',
        'requirements': ['Python', 'SQL']
    }
```

## Mocking External Services

### Mock API Calls
```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_job_scraper(mock_get):
    """Test job scraper with mocked API."""
    mock_response = Mock()
    mock_response.json.return_value = {'jobs': [...]}
    mock_get.return_value = mock_response
    
    result = scrape_jobs()
    assert len(result) > 0
```

### Mock File I/O
```python
from unittest.mock import mock_open, patch

@patch('builtins.open', mock_open(read_data='test data'))
def test_file_reading():
    """Test file reading with mock."""
    result = read_file('test.txt')
    assert 'test data' in result
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=automation
```

## Test Coverage

### Coverage Goals
- **Overall**: 80%+ coverage
- **Critical paths**: 100% coverage
- **Error handling**: 100% coverage
- **UI/glue code**: Lower priority

### Viewing Coverage
```bash
pytest --cov=automation --cov-report=html
open htmlcov/index.html
```

## Manual Testing

### Manual Test Checklist
- [ ] Run job scraper and verify output
- [ ] Generate tailored resume and review quality
- [ ] Generate outreach message and check personalization
- [ ] Update Excel file and verify data integrity
- [ ] Test error scenarios (bad input, network errors)
- [ ] Verify notifications work
- [ ] Check audit logging

### Manual Testing Procedures
See individual test files for detailed manual testing procedures.

## Test Maintenance

### When to Update Tests
- When adding new features
- When fixing bugs
- When refactoring code
- When behavior changes

### Test Hygiene
- Remove obsolete tests
- Update test data regularly
- Keep tests fast (< 1 second each)
- Fix flaky tests immediately
- Maintain test documentation

## Debugging Failed Tests

### Steps
1. **Read the error**: Understand what failed
2. **Run in isolation**: Run just that test
3. **Add prints**: Debug with print statements
4. **Use debugger**: Step through with pdb
5. **Check assumptions**: Verify test assumptions
6. **Simplify**: Reduce test to minimal failing case

### Using pdb
```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    result = function_to_test()
    assert result is not None
```

## Performance Testing

### Timing Tests
```python
import time

def test_performance():
    """Test that operation completes in reasonable time."""
    start = time.time()
    result = expensive_operation()
    duration = time.time() - start
    assert duration < 5.0  # Should complete in 5 seconds
```

### Load Testing
For API endpoints and batch operations, consider:
- Multiple concurrent requests
- Large data volumes
- Resource consumption

## Quality Standards

### Test Quality Metrics
- **Pass rate**: 100% before merge
- **Coverage**: 80%+ overall
- **Speed**: Test suite < 5 minutes
- **Flakiness**: 0 flaky tests
- **Maintainability**: Tests easy to update

## Resources

### Documentation
- pytest: https://docs.pytest.org/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Coverage.py: https://coverage.readthedocs.io/

### Tools
- pytest: Test framework
- pytest-cov: Coverage plugin
- pytest-mock: Mocking utilities
- pytest-xdist: Parallel test execution
- tox: Test multiple environments

## Support

For questions about testing:
1. Check test file docstrings
2. Review pytest documentation
3. Look at existing tests for examples
4. Ask for help in PR reviews
