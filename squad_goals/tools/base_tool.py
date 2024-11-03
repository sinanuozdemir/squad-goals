# base class for tools
import inspect
import io
from contextlib import redirect_stdout
from typing import Any
import json
class BaseTool:
    def __init__(self, name: str, description: str, **kwargs):
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
        help_string = help_string[help_string.find('\n') + 1:].strip()

        signature = inspect.signature(self.run)
        param_dict = {name: param.annotation for name, param in signature.parameters.items()}
        if param_dict:
            help_string += "\nParameters to include in Action Input dictionary:\n"
            for name, annotation in param_dict.items():
                if name == 'kwargs':
                    annotation = 'Any additional keyword arguments'
                help_string += f"\t{name}: {annotation}\n"
        else:
            help_string += "\nParameters to include in Action Input dictionary: None\n"

        # get the parameters and construct a sample call

        return help_string.strip()


class ReturnFinalAnswerTool(BaseTool):
    def __init__(self):
        super().__init__(
            "Return Final Answer Tool",
            "This tool returns the final answer to the task. Pass all inputs as {{\"final_answer\": \"your answer\"}}"
        )

    def run(self, final_answer: Any) -> Any:
        '''
        :param final_answer: The final answer to the task
        must pass final_answer as a string
        '''
        try:
            final_answer = json.dumps(final_answer)
        except:
            pass
        return final_answer
