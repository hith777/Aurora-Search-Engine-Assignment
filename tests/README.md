# Test Utilities

This directory contains testing and utility scripts for the Aurora Search Engine.

## Test Scripts

### `test_api.py`
Comprehensive API test suite that tests all endpoints, pagination, error handling, and includes performance testing.

**Usage:**
```bash
python tests/test_api.py
```

### `test_performance.py`
Performance testing script with detailed statistics and requirement verification.

**Usage:**
```bash
# Quick test
python tests/test_performance.py --quick

# Full test with multiple iterations
python tests/test_performance.py --query "hello" --iterations 20

# Test deployed API
python tests/test_performance.py --url https://aurora-search-engine-5bxb.onrender.com
```

### `test_api.sh`
Bash script for quick API testing.

**Usage:**
```bash
./tests/test_api.sh
```

### `test_deployed.sh`
Quick script to test deployed API speed.

**Usage:**
```bash
./tests/test_deployed.sh https://aurora-search-engine-5bxb.onrender.com hello
```

### `test_speed.html`
Browser-based speed testing tool. Open in a web browser to test API performance with a visual interface.

**Usage:**
Open `tests/test_speed.html` in your browser and enter the API URL.

## Utility Scripts

### `view_messages.py`
Interactive script to fetch and view messages from the API.

**Usage:**
```bash
python tests/view_messages.py
```

### `view_messages_simple.py`
Simple script to quickly view messages from the API.

**Usage:**
```bash
python tests/view_messages_simple.py
```
