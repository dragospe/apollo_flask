from apollo_flask import create_app

def test_config():
    """Test if the test configuration is getting passed properly."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
