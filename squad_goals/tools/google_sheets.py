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

    def run(self, data: List[List[str]]) -> Dict:
        """
        Runs the append operation.
        :param data: List of lists, where each inner list represents a row.
        :return: The response from the Sheets API.
        """
        return self.append_data(data)

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
