import json
import os
from typing import List, Dict, Optional

from .base_tool import BaseTool


class GoogleSpreadsheetTool(BaseTool):
    def __init__(
            self,
            spreadsheet_id: str,
            sheet_name: str = "Sheet1",
            credentials_json: Optional[Dict] = None,
            name: str = "Google Spreadsheet Tool",
            description: str = "This tool appends data to a Google Spreadsheet.",
            **kwargs
    ):
        try:
            from googleapiclient.discovery import build
            from google.oauth2.service_account import Credentials
        except ImportError:
            raise ImportError('Please install google-api-python-client with "pip install google-api-python-client"')
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.credentials_json = credentials_json
        if not self.credentials_json:
            # check GOOGLE_CREDENTIALS env
            try:
                self.credentials_json = json.load(open(os.environ['GOOGLE_CREDENTIALS']))
            except KeyError:
                raise ValueError("Please provide credentials_json or set GOOGLE_CREDENTIALS env variable")
        creds = Credentials.from_service_account_info(self.credentials_json)
        self.service = build('sheets', 'v4', credentials=creds)
        super().__init__(name, description, **kwargs)

    def append_data(self, data: List[List[str]]):
        """
        Appends data to the end of the sheet.
        :param data: List of lists, where each inner list represents a row.

        e.g. [['panda', 'red', 'bamboo'], ['dog', 'brown', 'bone']]
        """
        range_name = f"{self.sheet_name}!A1"
        body = {
            'values': data
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return result

    def get_sheet_data(self) -> List[List[str]]:
        """
        Gets all data from the sheet.
        :return: List of lists, where each inner list represents a row.
        """
        range_name = f"{self.sheet_name}"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])

    def find_in_column(self, search_value: str, column_name: str) -> List[int]:
        """
        Searches for a value in a specific column and returns the row indices where found.
        :param search_value: The value to search for
        :param column_name: The column header/name to search in
        :return: List of row indices where the value was found (0-based, excluding header row)
        """
        data = self.get_sheet_data()
        if not data:
            return []

        # Find the column index from the header row
        headers = data[0]
        try:
            column_index = headers.index(column_name)
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found in sheet headers")

        # Search for the value in the specified column
        matches = []
        for i, row in enumerate(data[1:], 1):  # Start from 1 to skip header row
            if len(row) > column_index and row[column_index] == search_value:
                matches.append(i)

        return matches

    def run(self, data: List[List[str]], action: str = "append", **kwargs) -> Dict:
        """
        Runs the specified operation.
        :param data: List of lists, where each inner list represents a row.
        :param action: The action to perform ("append" or "search")
        :Additional arguments for specific actions
            For "search" action:
                - search_value: The value to search for
                - column_name: The column header/name to search in
            For "append" action:
                - None
        :return: The response from the operation
        """
        if action == "append":
            return self.append_data(data)
        elif action == "search":
            search_value = kwargs.get('search_value')
            column_name = kwargs.get('column_name')
            if not search_value or not column_name:
                raise ValueError("search_value and column_name are required for search action")
            matches = self.find_in_column(search_value, column_name)
            return {"matches": matches, "total_matches": len(matches)}
        else:
            raise ValueError(f"Unknown action: {action}")

    # method to add a list of data at a specific range
    def add_data_at_range(self, data: List[List[str]], range_name: str):
        """
        Appends data to the end of the sheet.
        :param data: List of lists, where each inner list represents a row.
        :param range_name: The range to add the data to, e.g. "Sheet1!A1"
        """
        body = {
            'values': data
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return result
