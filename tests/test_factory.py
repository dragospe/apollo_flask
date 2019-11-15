from apollo_flask import create_app

def test_config():
    """Test if the test configuration is getting passed properly."""
    assert not create_app().testing
    assert create_app({'TESTING': True, 'ENGINE':'mock_engine', 'DATABASE_URI':'postgresql://mock_db_uri.com'}).testing
