# base class for tools
import io
from contextlib import redirect_stdout


class BaseTool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self):
        raise NotImplementedError("Method run not implemented")

    def _describe_run(self):
        # Create an in-memory text stream
        help_output = io.StringIO()

        # Redirect stdout to the text stream and call help
        with redirect_stdout(help_output):
            help(self.run)

        # Get the content of the help output as a string
        help_string = help_output.getvalue()

        # Close the StringIO object
        help_output.close()

        # remove the first line of the help string
        help_string = help_string[help_string.find('\n') + 1:]

        return help_string.strip()


class ReturnFinalAnswerTool(BaseTool):
    def __init__(self):
        super().__init__("Return Final Answer Tool", "This tool returns the final answer to the task")

    def run(self, final_answer: str):
        return final_answer
