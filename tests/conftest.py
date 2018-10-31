import pytest


@pytest.fixture
def app():
    from pdf_microservice import server
    server.app.testing = True
    client = server.app.test_client()
    return client
