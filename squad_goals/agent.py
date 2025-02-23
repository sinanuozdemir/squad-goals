import datetime
import json
import re
from copy import copy
from typing import List, Dict, Tuple
from typing import Optional

from squad_goals.conversation.models import Conversation, Message
from .llms.base_llm import LLM
from .task import Task
from .tools.base_tool import BaseTool, ReturnFinalAnswerTool
from .utils import extract_json_from_string

OBSERVATION_TOKEN = "Observation:"
NEXT_THOUGHT_TOKEN = "Next Thought:"
param_value_dict = json.dumps({"param": "value"})
final_answer_dict = json.dumps({"final_answer": "the final answer to return to the user"})
PROMPT_TEMPLATE = """Today is {today} and you can use tools to get new information. 
Respond to the user's input as best as you can using the following tools:

{tool_description}

First Thought:
Thought: comment on what you want to do next.
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action (must be a single line json loadable dictionary of parameters e.g. {param_value_dict})
Observation: the result of the action
Next Thought: (7 thoughts left)
Thought: Now comment on what you want to do next.
Action: the next action to take, exactly one element of [{tool_names}]
Action Input: the input to the next action (must be a single line json loadable dictionary of parameters e.g. {param_value_dict})
Observation: the result of the next action
... (this Thought/Action/Action Input/Observation repeats until you are sure of the answer)
Next Thought: (6 thoughts left)
Thought: Now comment on what you want to do next.
Action: the next action to take, exactly one element of [{tool_names}]
Action Input: the input to the next action (must be a single line json loadable dictionary of parameters e.g. {param_value_dict})
Observation: the result of the next action
Next Thought: (5 thoughts left)
Thought: I can finally return the final answer
Action: Return Final Answer Tool
Action Input: {final_answer_dict}

YOU MUST END WITH THE "Return Final Answer Tool" TO RETURN THE FINAL ANSWER TO THE USER and the final answer must be in the "Action Input" field.

Begin:

##########
START GOAL
##########
{goal}
##########
END GOAL
##########

First Thought:
{previous_responses}
"""


class Agent():
    def __init__(self, llm: LLM, tools: List[BaseTool] = [],
                 prompt_template: str = PROMPT_TEMPLATE,
                 max_loops: int = 5,
                 verbose: bool = False,
                 debug: bool = False,
                 tool_eval_mode: bool = False,
                 conversation: Optional[Conversation] = None,
                 name: str = 'Agent',
                 use_conversation: bool = False
                 ):
        self.llm = llm  # Language model we are using
        self.tools = tools  # List of tools the agent can use
        if not any(isinstance(tool, ReturnFinalAnswerTool) for tool in tools):  # Ensure we have a final answer tool
            tools.append(ReturnFinalAnswerTool())
        self.prompt_template = copy(prompt_template)  # Template for the prompt
        self.max_loops = max_loops  # Maximum number of loops to run
        self.ai_responses = []  # List of responses from the AI
        self.verbose = verbose  # Verbose mode
        self.debug = debug  # Debug mode
        self.errors_encountered = []  # List of errors encountered
        self.tools_selected = []  # List of tools selected
        self.tools_used = []  # List of tools used
        self.tool_eval_mode = tool_eval_mode  # If True, the tools will not be run
        self.stop_pattern = [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}']  # Stop pattern for the LLM
        self.conversation = conversation  # Conversation object
        if not self.conversation:
            self.conversation = Conversation(messages=[])
        self.name = name  # Name of the agent
        self.use_conversation = use_conversation  # If True, the agent will use the conversation object

    @property
    def tool_description(self) -> str:
        return "\n".join(
            [f"{tool.name}: {tool.description}. how to run: {tool._describe_run()}" for tool in self.tools])

    @property
    def quoted_tool_names(self) -> str:
        return ", ".join([f'"{tool.name}"' for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, BaseTool]:
        return {tool.name: tool for tool in self.tools}

    def run(self, task: Task, yield_events=False):
        previous_responses = copy(self.ai_responses)
        num_loops = 0
        prompt = copy(self.prompt_template).format(
            today=datetime.date.today(),
            tool_description=self.tool_description,
            tool_names=self.quoted_tool_names,
            goal=task.goal,
            previous_responses='{previous_responses}',
            final_answer_dict='{final_answer_dict}',
            param_value_dict='{param_value_dict}'
        )

        def execute_steps():
            nonlocal num_loops
            while num_loops < self.max_loops:
                num_loops += 1
                curr_prompt = prompt.replace(
                    '{previous_responses}', '\n'.join(previous_responses).strip(),
                ).replace(
                    '{final_answer_dict}', final_answer_dict
                ).replace('{param_value_dict}', param_value_dict)

                generated, tool, tool_input = self.decide_next_action(curr_prompt)
                yield dict(event='next_agent_action', loop=num_loops, tool=tool, tool_input=tool_input,
                           generated=generated)

                self.tools_selected.append(tool)
                if tool not in self.tool_by_names:
                    self.errors_encountered.append(ValueError(f"Unknown tool: {tool}"))
                    yield dict(event='error', message=f"Unknown tool: {tool}")
                    continue

                try:
                    yield dict(event='tool_selected', tool=tool)
                    tool_obj = self.tool_by_names[tool]
                    tool_result = tool_obj.run(**(
                                tool_input or {})) if not self.tool_eval_mode else 'Tool evaluation mode is on. No tool will be run.'
                    self.tools_used.append(tool)
                    yield dict(event='tool_run', tool=tool, tool_input=tool_input, tool_result=tool_result)
                except Exception as e:
                    self.errors_encountered.append(e)
                    yield dict(event='tool_error', message=f'Error from tool: {e}')
                    continue

                yield dict(event='tool_result', tool=tool, result=tool_result)

                generated += f"\n{OBSERVATION_TOKEN} {tool_result}\nNext Thought: ({self.max_loops - num_loops} thoughts left)"
                self.ai_responses.append(generated.strip())
                previous_responses.append(generated)

                if tool == 'Return Final Answer Tool':
                    task.raw_output = tool_result
                    task.completed = True
                    task.succeeded = True
                    prompt_final = prompt.replace(
                        '{previous_responses}', '\n'.join(previous_responses).strip()
                    ).replace(
                        '{final_answer_dict}', final_answer_dict
                    ).replace(
                        '{param_value_dict}', param_value_dict
                    )
                    if self.use_conversation:
                        self.conversation.messages.append(
                            Message(content=prompt_final, source=self.name, role='assistant'))
                    yield dict(event='agent_completed', final_answer=tool_result)
                    return

            yield dict(event='max_loops_reached', message=f'Max loops ({self.max_loops}) reached.')

        return execute_steps() if yield_events else list(execute_steps())

    def decide_next_action(self, prompt: str) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        if self.conversation and self.use_conversation:
            messages = self.conversation.messages_as_dicts() + messages
        generated = self.llm.generate(
            messages,
            stop=self.stop_pattern)

        tool, tool_input = self._parse(generated)
        if self.debug:
            print('raw tool', tool)
            print('raw tool_input', tool_input)
        try:
            tool_input = extract_json_from_string(tool_input)  # Attempt to load as JSON
        except Exception as e:
            self.errors_encountered.append(e)  # Add error to the list of errors
            if self.verbose:
                print(f"\tError loading JSON from tool_input: {e}")
            tool_input = None  # Set to None if we can't load as JSON
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        if self.debug:
            print('generated', generated)
        regex = r"Action:\s*\[?(.*?)\]?\s*[\r\n]+Action Input:.*?({[^{}]*({[^{}]*})*[^{}]*})"
        match = re.search(regex, generated, re.DOTALL)
        if not match:  # special case: generated is json loadable and has the "final_answer" key, then it is the final answer
            try:
                tool_input = extract_json_from_string(generated)
                if 'final_answer' in tool_input:
                    return 'Return Final Answer Tool', json.dumps(tool_input)
            except:
                pass
            self.errors_encountered.append(
                ValueError(f"Output of LLM is not parsable for next tool use: `{generated}`"))
            if self.verbose:
                print(f"Error parsing generated output: {generated}")
            # if not debug, add this as the observation so the agent can try again
            tool = F'TOOL ERROR. MAKE SURE TO STATE A TOOL NAME FROM THE LIST: {self.quoted_tool_names}. If you are trying to end the conversation or you think the task is already solved, please use the "Action: Return Final Answer Tool" and give the final answer this way.'
            tool_input = tool
        else:
            tool = match.group(1).strip()
            tool_input = match.group(2).split(OBSERVATION_TOKEN)[0].split(NEXT_THOUGHT_TOKEN)[0].strip()
        return tool, tool_input.strip(" ").strip('"')
