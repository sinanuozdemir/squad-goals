from .utils import extract_json_from_string


class Task:
    def __init__(self, name: str, goal: str, output_format: str = 'text') -> None:
        self.name = name
        self.goal = goal
        self.raw_output = None
        self.parsed_output = None
        self.output_format = output_format
        self.completed = False
        self.succeeded = False

    def __str__(self) -> str:
        return f"{self.name}: {self.goal}"

    def parse_output(self):
        if not self.raw_output:
            return
        if self.output_format == 'json':
            self.parsed_output = extract_json_from_string(self.raw_output)  # Load as JSON
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

    def __repr__(self) -> str:
        return f"Task({self.name[:100]}.., Goal: {self.goal[:50]}.., {self.output_format}, Completed: {self.completed}). Succeeded: {self.succeeded}"
