import sys
from io import StringIO

from .base_tool import BaseTool


class PythonREPLTool(BaseTool):
    def __init__(self, **kwargs):
        self.name = "Python REPL Tool"
        self.description = "This tool runs Python code in a REPL and returns the output. Use this to make tasks more efficient or just to run and test code."
        super().__init__(self.name, self.description, **kwargs)

    def run(self, command: str) -> str:
        """
        Run command with own globals/locals and returns anything printed.
        :param command: The Python command to run. Always end with a print statement to show the output like "print(output)"
        """
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command)
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            output = str(e)
        return output.strip()
