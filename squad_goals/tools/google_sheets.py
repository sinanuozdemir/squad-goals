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
        
        # Extract the values and determine the range size
        values = result.get('values', [])
        start_cell, end_cell = range_name.split('!')[1].split(':')
        start_row = int(''.join(filter(str.isdigit, start_cell)))
        end_row = int(''.join(filter(str.isdigit, end_cell)))
        range_length = end_row - start_row + 1
        
        # Append empty lists to match the length of the range
        while len(values) < range_length:
            values.append([])
        
        return values

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

    def _col_index_to_letter(self, index: int) -> str:
        ''' Convert a column index to a letter e.g. 1 -> A, 2 -> B, 26 -> Z, 27 -> AA, 30 -> AD'''
        letter = ''
        while index > 0:
            letter = chr(65 + (index - 1) % 26) + letter
            index = (index - 1) // 26
        return letter

    def find_in_column(self, search_value: str, column_name: str) -> List[int]:
        """
        Searches for a value in a specific column and returns the row indices where found.
        :param search_value: The value to search for
        :param column_name: The column header/name to search in
        :return: List of row indices where the value was found (0-based, excluding header row)
        """
        # Use describe_columns_and_rows to get headers
        description = self.describe_columns_and_rows()
        column_map = description.get('column_map', {})
        num_rows = description.get('rows', 0)
        
        # Find the column index from the column map
        try:
            column_index = list(column_map.values()).index(column_name)
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found in sheet headers")
        
        # Convert column index to letter using _col_index_to_letter
        column_letter = self._col_index_to_letter(column_index + 1)  # +1 because _col_index_to_letter is 1-based
        print(f'column_letter: {column_letter}')
        
        # Get all data from the sheet
        range_name = f"{self.sheet_name}!{column_letter}{self.header_row + 1}:{column_letter}{num_rows}"
        data = self.get_data_in_range(range_name)
        print(f'data: {data}')
        if not data:
            return []

        # Search for the value in the specified column
        matches = []
        for i, row in enumerate(data, 1):  # Start from 1 to skip header row
            if search_value == '' and not row:
                matches.append(i)
            elif row and row[0] == search_value:
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

    def run(self, action: str = "append_to_sheet", **kwargs) -> Dict:
        """
        Executes specified actions on the Google Spreadsheet.

        :param action: The action to perform ("append_to_sheet", "search", "insert_into_cell", "get_data_in_range", "describe").
        :Additional arguments for each specific action:
            - "search": 
                "search" will return the row indices where the search_value is found in the column_name.
                Requires 'search_value' and 'column_name'. Example: {"action": "search", "search_value": "John", "column_name": "Name"}
            - "append_to_sheet":
                "append_to_sheet" will append the data to the end of the sheet.
                Requires 'data'. Example: {"action": "append_to_sheet", "data": [["John", "Doe", "john.doe@example.com"], ["Jane", "Smith", "jane.smith@example.com"]]}
            - "insert_into_cell": 
                "insert_into_cell" will insert the value into the specified cell.
                Requires 'value' and 'cell'. Example: {"action": "insert_into_cell", "value": "New Value", "cell": "A1"}
            - "get_data_in_range": 
                "get_data_in_range" will return the data in the specified range.
                Requires 'range_name'. Example: {"action": "get_data_in_range", "range_name": "Sheet1!A1:B2"} or {"action": "get_data_in_range",    "range_name": "Contacts!A12:G28"}
            - "describe": 
                "describe" will return the number of columns and rows in the sheet.
                No additional arguments. Example: {"action": "describe"}
        :return: The result of the operation.
        """
        data = kwargs.get('data')
        if action == "append_to_sheet":
            return self.append_data(data)
        elif action == "describe":
            return self.describe_columns_and_rows()
        elif action == "search":
            search_value = kwargs.get('search_value')
            column_name = kwargs.get('column_name')
            if search_value is None or column_name is None:
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
