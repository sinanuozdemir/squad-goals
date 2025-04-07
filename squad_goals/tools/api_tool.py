import re
from copy import copy

import requests

from .base_tool import BaseTool


class APITool(BaseTool):
    def __init__(
            self,
            api_url: str,
            api_key: str,
            api_header_key: str = 'Authorization',
            api_header_value: str = 'Bearer ',
            name: str = "API Tool",
            api_method='POST',
            description: str = "This tool uses an API to get information",
            static_kwargs: dict = None,
            **kwargs
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.api_header_key = api_header_key
        self.api_header_value = api_header_value
        self.api_method = api_method.upper()
        # using regex, check for {business_id} or other variables in the url and save
        re_pattern = r'{(\w+)}'
        self.url_variables = re.findall(re_pattern, api_url)
        self.static_kwargs = static_kwargs

        super().__init__(name, description, **kwargs)

    def run(self, api_payload: dict = None, **kwargs) -> dict:
        headers = {
            self.api_header_key: f"{self.api_header_value}{self.api_key}"
        } if self.api_key else {}

        # Replace URL variables with values from kwargs, raise error if not found
        kwargs.update(self.static_kwargs or {})
        if len(set(self.url_variables) - set(kwargs.keys())) > 0:
            raise ValueError(f"URL variables {set(self.url_variables) - set(kwargs.keys())} not found in kwargs")

        url_to_use = copy(self.api_url)
        for url_var in self.url_variables:
            url_to_use = url_to_use.replace(f"{{{url_var}}}", kwargs[url_var])

        # Use api_payload as query parameters for GET requests
        if self.api_method == 'GET' and api_payload:
            response = requests.get(url_to_use, headers=headers, params=api_payload)
        else:
            response = getattr(requests, self.api_method.lower())(url_to_use, headers=headers, json=api_payload)

        return response.json()

    # base tool has _describe_run, but add the url variables here so they know to set it
    def _describe_run(self):
        base_description = super()._describe_run()
        return f"{base_description}\nURL Variables that must be passed as well: {', '.join(self.url_variables)}"


class ApolloTool(APITool):
    """
    Tool for interacting with the Apollo.io API.
    Enables operations like searching contacts and managing contact data.
    """
    
    def __init__(
            self,
            api_key: str,
            name: str = "Apollo Tool",
            description: str = "Tool for searching and managing contacts using the Apollo.io API",
            **kwargs
    ):
        # Apollo.io API typically uses a simple API key in the headers
        super().__init__(
            api_url="https://api.apollo.io/api/v1/{endpoint}",
            api_key=api_key,
            api_header_key="X-Api-Key",  # Apollo uses X-Api-Key header for authentication
            api_header_value="",  # No prefix needed for Apollo API
            name=name,
            description=description,
            api_method='POST',
            static_kwargs=None,
            **kwargs
        )
    
    def super_run(self, **kwargs):
        """Call the parent class run method to avoid recursion"""
        return super().run(**kwargs)
    
    def search_contacts(self, search_params: dict):
        """
        Search for contacts in Apollo.io with the given parameters.
        
        Args:
            search_params (dict): Parameters for filtering contacts
            
        Returns:
            dict: API response with contact data
        """
        return self.super_run(
            api_payload=search_params,
            endpoint="contacts/search"
        )
    
    def create_contact(self, contact_data: dict):
        """
        Create a new contact in Apollo.io.
        
        Args:
            contact_data (dict): Data for the new contact
            
        Returns:
            dict: API response with the created contact
        """
        return self.super_run(
            api_payload=contact_data,
            endpoint="contacts"
        )
    
    def get_contact(self, contact_id: str):
        """
        Get information about a specific contact.
        
        Args:
            contact_id (str): ID of the contact to retrieve
            
        Returns:
            dict: API response with contact details
        """
        return self.super_run(
            api_payload={"id": contact_id},
            endpoint=f"contacts/{contact_id}"
        )
    
    def update_contact(self, contact_id: str, update_data: dict):
        """
        Update an existing contact in Apollo.io.
        
        Args:
            contact_id (str): ID of the contact to update
            update_data (dict): New data for the contact
            
        Returns:
            dict: API response with the updated contact
        """
        payload = {"id": contact_id, **update_data}
        return self.super_run(
            api_payload=payload,
            endpoint=f"contacts/{contact_id}"
        )
        
    def run(self, action: str = "search_contacts", **kwargs) -> dict:
        """
        Executes specified actions on the Apollo.io API.

        :param action: The action to perform ("search_contacts", "create_contact", "get_contact", "update_contact").
        :Additional arguments for each specific action:
            - "search_contacts": 
                "search_contacts" will search for contacts with the given parameters.
                Requires 'search_params'. Example: {"action": "search_contacts", "search_params": {"first_name": "John"}}
            - "create_contact":
                "create_contact" will create a new contact.
                Requires 'contact_data'. Example: {"action": "create_contact", "contact_data": {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}}
            - "get_contact": 
                "get_contact" will retrieve information about a specific contact.
                Requires 'contact_id'. Example: {"action": "get_contact", "contact_id": "123456"}
            - "update_contact": 
                "update_contact" will update an existing contact.
                Requires 'contact_id' and 'update_data'. Example: {"action": "update_contact", "contact_id": "123456", "update_data": {"first_name": "Jane"}}
        :return: The result of the operation.
        """
        if action == "search_contacts":
            search_params = kwargs.get('search_params')
            if not search_params:
                raise ValueError("search_params is required for search_contacts action")
            return self.search_contacts(search_params)
        elif action == "create_contact":
            contact_data = kwargs.get('contact_data')
            if not contact_data:
                raise ValueError("contact_data is required for create_contact action")
            return self.create_contact(contact_data)
        elif action == "get_contact":
            contact_id = kwargs.get('contact_id')
            if not contact_id:
                raise ValueError("contact_id is required for get_contact action")
            return self.get_contact(contact_id)
        elif action == "update_contact":
            contact_id = kwargs.get('contact_id')
            update_data = kwargs.get('update_data')
            if not contact_id or not update_data:
                raise ValueError("contact_id and update_data are required for update_contact action")
            return self.update_contact(contact_id, update_data)
        else:
            raise ValueError(f"Unknown action: {action}")
