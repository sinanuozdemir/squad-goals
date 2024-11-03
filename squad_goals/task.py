import json
import re


class Task:
    def __init__(self, name: str, goal: str, output_format: str = 'text', completed: bool = False) -> None:
        self.name = name
        self.goal = goal
        self.raw_output = None
        self.parsed_output = None
        self.output_format = output_format
        self.completed = completed

    def __str__(self) -> str:
        return f"{self.name}: {self.goal}"

    def parse_output(self):
        if not self.raw_output:
            return
        if self.output_format == 'json':

            # Extract JSON-like content between brackets
            json_matches = re.findall(r'\[\s*(?:[^\[\]]*?)\]', self.raw_output, re.DOTALL)

            # Assume largest JSON is the most complete one
            largest_json = max(json_matches, key=len)

            # Load as JSON
            self.parsed_output = json.loads(largest_json)
        elif self.output_format == 'text':
            self.parsed_output = self.raw_output
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")
        return self.parsed_output

    @property
    def output(self):
        if not self.parsed_output:
            self.parse_output()
        return self.parsed_output
