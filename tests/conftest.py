# tests/conftest.py


def pytest_configure(config):
    # Register custom markers
    config.addinivalue_line("markers", "docker: mark test to run with Docker/Postgres")
    config.addinivalue_line("markers", "integration: mark test as integration test")
