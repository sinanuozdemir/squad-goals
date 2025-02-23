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
            header_row: int = 0,
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
        self.header_row = header_row
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

    def get_data_in_range(self, range_name: str) -> List[List[str]]:
        """
        Gets all data from a specific range.
        :param range_name: The range to get data from, e.g. "Sheet1!A1:B2" or "Dashboard!A3:A"
        :return: List of lists, where each inner list represents a row.
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])

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
        headers = data[self.header_row or 0]
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

    def describe_columns_and_rows(self) -> Dict:
        '''
        Describes the columns and rows in the sheet.

        :return: A dictionary containing the number of columns and rows in the sheet.
        e.g. {'columns': 5, 'rows': 10, 'sheet_name': 'Sheet1', 'spreadsheet_id': 'abc123', 'column_map': {'A': 'Name', 'B': 'Age'}}
        '''
        data = self.get_sheet_data()
        data = [_ for _ in data if _]
        headers = data[self.header_row or 0]
        if not data:
            return {'columns': 0, 'rows': 0, 'sheet_name': self.sheet_name, 'spreadsheet_id': self.spreadsheet_id}
        n_cols, n_rows = len(headers), len(data)
        column_map = {chr(65 + i): col for i, col in enumerate(headers)}
        return {'columns': n_cols, 'rows': n_rows, 'sheet_name': self.sheet_name, 'spreadsheet_id': self.spreadsheet_id,
                'column_map': column_map}

    def insert_into_cell(self, value: str, cell: str):
        """
        Inserts a value into a specific cell.
        :param value: The value to insert
        :param cell: The cell to insert the value into, e.g. "A1"
        """
        range_name = f"{self.sheet_name}!{cell}"
        body = {
            'values': [[value]]
        }
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()
        return result

    def run(self, data: List[List[str]] = None, action: str = "append", **kwargs) -> Dict:
        """
        Runs various actions on the Google Spreadsheet.
        "describe": Describes the columns and rows in the sheet. Use this to get the column names or just to understand the sheet.
        "search": Searches for a value in a specific column and returns the row indices where found.
        "append_to_sheet": Appends data to the end of the sheet.
        "insert_into_cell": Inserts a value into a specific cell.
        "get_data_in_range": Gets all data from a specific range.
        :param data: List of lists, where each inner list represents a row.
        :param action: The action to perform ("append_to_sheet", "search", "insert_into_cell", "get_data_in_range", or "describe")
        :Additional arguments for specific actions
            For action="describe":
                - None
            For action="search":
                - search_value: The value to search for
                - column_name: The column header/name to search in
            For action="append_to_sheet":
                - None
            For action="insert_into_cell":
                - value: The value to insert
                - cell: The cell to insert the value into, e.g. "A1"
            For action="get_data_in_range":
                - range_name: The range to get data from, e.g. "Sheet1!A1:B2". For example if you need data from the 3rd column, you can use "Sheet1!A3:A"
        :return: The response from the operation
        """
        if action == "append_to_sheet":
            return self.append_data(data)
        elif action == "describe":
            return self.describe_columns_and_rows()
        elif action == "search":
            search_value = kwargs.get('search_value')
            column_name = kwargs.get('column_name')
            if not search_value or not column_name:
                raise ValueError("search_value and column_name are required for search action")
            matches = self.find_in_column(search_value, column_name)
            return {"matches": matches, "total_matches": len(matches)}
        elif action == "insert_into_cell":
            value = kwargs.get('value')
            cell = kwargs.get('cell')
            if not value or not cell:
                raise ValueError("value and cell are required for insert_into_cell action")
            return self.insert_into_cell(value, cell)
        elif action == "get_data_in_range":
            range_name = kwargs.get('range_name')
            if not range_name:
                raise ValueError("range_name is required for get_data_in_range action")
            return self.get_data_in_range(range_name)
        else:
            raise ValueError(f"Unknown action: {action}")

    # method to add a list of data at a specific range
    def add_data_at_range(self, data: List[List[str]], range_name: str):
        """
        Appends data to the end of the sheet.
        :param data: List of lists, where each inner list represents a row.
        :param range_name: The range to add the data to, e.g. "Sheet1!A1" or "Dashboard!A3" or "Sheet6!A1:B2"
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
