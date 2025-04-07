import unittest
from unittest.mock import patch, MagicMock
import json
import os
from dotenv import load_dotenv
from squad_goals.tools import ApolloTool

class TestApolloTool(unittest.TestCase):
    def setUp(self):
        # Use API key from environment variable
        self.api_key = os.getenv("APOLLO_IO_KEY", "test_api_key")
        self.apollo_tool = ApolloTool(api_key=self.api_key)
    
    def test_initialization(self):
        """Test proper initialization of the ApolloTool."""
        self.assertEqual(self.apollo_tool.api_key, self.api_key)
        self.assertEqual(self.apollo_tool.api_url, "https://api.apollo.io/api/v1/{endpoint}")
        self.assertEqual(self.apollo_tool.api_header_key, "X-Api-Key")
        self.assertEqual(self.apollo_tool.api_header_value, "")
        self.assertEqual(self.apollo_tool.api_method, "POST")
        self.assertEqual(self.apollo_tool.name, "Apollo Tool")
    
    @patch('requests.post')
    def test_search_contacts(self, mock_post):
        """Test the search_contacts method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contacts": [
                {"id": "1", "first_name": "John", "last_name": "Doe"},
                {"id": "2", "first_name": "Jane", "last_name": "Smith"}
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the method
        search_params = {
            "q_organization_domains": ["example.com"],
            "page": 1
        }
        result = self.apollo_tool.search_contacts(search_params)
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/search")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], search_params)
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_create_contact(self, mock_post):
        """Test the create_contact method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "1", "first_name": "John", "last_name": "Doe"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }
        result = self.apollo_tool.create_contact(contact_data)
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], contact_data)
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_get_contact(self, mock_post):
        """Test the get_contact method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "123", "first_name": "John", "last_name": "Doe"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_id = "123"
        result = self.apollo_tool.get_contact(contact_id)
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/123")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], {"id": "123"})
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_update_contact(self, mock_post):
        """Test the update_contact method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "123", "first_name": "John", "last_name": "Smith"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_id = "123"
        update_data = {"last_name": "Smith"}
        result = self.apollo_tool.update_contact(contact_id, update_data)
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/123")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], {"id": "123", "last_name": "Smith"})
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_run_search_contacts(self, mock_post):
        """Test the run method with search_contacts action."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contacts": [
                {"id": "1", "first_name": "John", "last_name": "Doe"},
                {"id": "2", "first_name": "Jane", "last_name": "Smith"}
            ]
        }
        mock_post.return_value = mock_response
        
        # Call the method
        search_params = {
            "q_organization_domains": ["example.com"],
            "page": 1
        }
        result = self.apollo_tool.run(
            action="search_contacts",
            search_params=search_params
        )
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/search")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], search_params)
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_run_create_contact(self, mock_post):
        """Test the run method with create_contact action."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "1", "first_name": "John", "last_name": "Doe"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        }
        result = self.apollo_tool.run(
            action="create_contact",
            contact_data=contact_data
        )
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], contact_data)
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_run_get_contact(self, mock_post):
        """Test the run method with get_contact action."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "123", "first_name": "John", "last_name": "Doe"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_id = "123"
        result = self.apollo_tool.run(
            action="get_contact",
            contact_id=contact_id
        )
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/123")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], {"id": "123"})
        self.assertEqual(result, mock_response.json.return_value)
    
    @patch('requests.post')
    def test_run_update_contact(self, mock_post):
        """Test the run method with update_contact action."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "contact": {"id": "123", "first_name": "John", "last_name": "Smith"}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        contact_id = "123"
        update_data = {"last_name": "Smith"}
        result = self.apollo_tool.run(
            action="update_contact",
            contact_id=contact_id,
            update_data=update_data
        )
        
        # Assertions
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.apollo.io/api/v1/contacts/123")
        self.assertEqual(call_args[1]['headers'], {"X-Api-Key": self.api_key})
        self.assertEqual(call_args[1]['json'], {"id": "123", "last_name": "Smith"})
        self.assertEqual(result, mock_response.json.return_value)
    
    def test_run_invalid_action(self):
        """Test the run method with an invalid action."""
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="invalid_action")
        
        self.assertEqual(str(context.exception), "Unknown action: invalid_action")
    
    def test_run_missing_parameters(self):
        """Test the run method with missing required parameters."""
        # Test missing search_params
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="search_contacts")
        self.assertEqual(str(context.exception), "search_params is required for search_contacts action")
        
        # Test missing contact_data
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="create_contact")
        self.assertEqual(str(context.exception), "contact_data is required for create_contact action")
        
        # Test missing contact_id
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="get_contact")
        self.assertEqual(str(context.exception), "contact_id is required for get_contact action")
        
        # Test missing contact_id and update_data
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="update_contact")
        self.assertEqual(str(context.exception), "contact_id and update_data are required for update_contact action")
        
        # Test missing update_data
        with self.assertRaises(ValueError) as context:
            self.apollo_tool.run(action="update_contact", contact_id="123")
        self.assertEqual(str(context.exception), "contact_id and update_data are required for update_contact action")

if __name__ == "__main__":
    unittest.main() 