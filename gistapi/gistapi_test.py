import unittest
from gistapi import app,gists_for_user

class TestGistSearchAPI(unittest.TestCase):

    def test_valid_username(self):
        """Test that the function returns a valid response for a valid username."""
        response = gists_for_user('octocat',1)
        self.assertIsInstance(response, list)
    
    def test_invalid_username(self):
        """Test that the function raises an exception for an invalid username."""
        with self.assertRaises(Exception):
            gists_for_user('nonexistentuser',1)

    def test_search_with_valid_input(self):
        response = app.test_client().post('/api/v1/search', json={'username': 'testuser', 'pattern': 'test'})
        self.assertIn(b'success', response.data)
        self.assertIn(b'testuser', response.data)
        self.assertIn(b'test', response.data)
        
    def test_search_with_invalid_username(self):
        response = app.test_client().post('/api/v1/search', json={'username': 'invalid_user', 'pattern': 'test'})
        self.assertIn(b'error', response.data)

    def test_search_with_missing_username(self):
        response = app.test_client().post('/api/v1/search', json={'pattern': 'inkxus'})
        self.assertIn(b'error', response.data)
        


if __name__ == '__main__':
    unittest.main()
