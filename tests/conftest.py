# tests/conftest.py

import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
def db():
    """Base de datos Mongo en memoria (mongomock) para tests de repositorios."""
    return AsyncMongoMockClient()["winsports_test"]
