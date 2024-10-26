import datetime
import re
from copy import copy
from typing import List, Dict, Tuple
from .task import Task
from .llms.base_llm import LLM
from .tools.base_tool import BaseTool, ReturnFinalAnswerTool

FINAL_ANSWER_TOKEN = "Assistant Response:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PROMPT_TEMPLATE = """Today is {today} and you can use tools to get new information. Respond to the user's input as best as you can using the following tools:

{tool_description}

You must follow the following format until you have enough information to respond to the user's input:

User Input: the input task you must address
Thought: comment on what you want to do next.
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: Now comment on what you want to do next.
Action: the next action to take, exactly one element of [{tool_names}]
Action Input: the input to the next action
Observation: the result of the next action
Thought: Now comment on what you want to do next.
... (this Thought/Action/Action Input/Observation repeats until you are sure of the answer)
Assistant Thought: I have enough information to respond to the user's input.
Assistant Response: your final answer to the original input task

You MUST end with "Assistant Thought:" and "Assistant Response:"

Begin:

{previous_responses}
"""


class Agent():
    def __init__(self, llm: LLM, tools: List[BaseTool], prompt_template: str = PROMPT_TEMPLATE, max_loops: int = 5,
                 stop_pattern: List[str] = [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}'],
                 verbose: bool = False):
        self.llm = llm
        self.tools = tools
        if not any(isinstance(tool, ReturnFinalAnswerTool) for tool in tools):
            tools.append(ReturnFinalAnswerTool())
        self.prompt_template = prompt_template
        self.max_loops = max_loops
        self.stop_pattern = stop_pattern
        self.ai_responses = []
        self.verbose = verbose

    @property
    def tool_description(self) -> str:
        return "\n".join([f"{tool.name}: {tool.description}. how to run: {tool._describe_run()}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        return ", ".join([tool.name for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, BaseTool]:
        return {tool.name: tool for tool in self.tools}

    def run(self, task: Task):
        self.ai_responses.append(f'User Input: {task.goal}')
        previous_responses = copy(self.ai_responses)
        num_loops = 0
        prompt = copy(self.prompt_template).format(
            today=datetime.date.today(),
            tool_description=self.tool_description,
            tool_names=self.tool_names,
            question=task.goal,
            previous_responses='{previous_responses}'
        )
        if self.verbose:
            print('------')
            print(prompt.format(previous_responses=''))
            print('------')
        while num_loops < self.max_loops:
            num_loops += 1
            curr_prompt = prompt.format(previous_responses='\n'.join(previous_responses))
            generated, tool, tool_input = self.decide_next_action(curr_prompt)
            if self.verbose:
                print('------')
                print('CURR PROMPT')
                print('------')
                print(curr_prompt)
                print('------')
                print('------')
                print('RAW GENERATED')
                print('------')
                print(generated)
                print('------')
            if tool == 'Assistant Response':
                if self.verbose:
                    print('------')
                    print('FINAL PROMPT')
                    print('------')
                    print(curr_prompt)
                    print('------')
                self.ai_responses.append(f'Assistant Response: {tool_input}')
                return tool_input
            if tool not in self.tool_by_names:
                raise ValueError(f"Unknown tool: {tool}")
            if self.verbose:
                print('tool_input', tool_input)
            tool_result = self.tool_by_names[tool].run(tool_input)
            generated += f"\n{OBSERVATION_TOKEN} {tool_result}\n"
            self.ai_responses.append(generated.strip())
            if self.verbose:
                print('------')
                print('PARSED GENERATED')
                print('------')
                print(generated)
                print('------')
            previous_responses.append(generated)

    def decide_next_action(self, prompt: str) -> str:
        generated = self.llm.generate(
            [{'role': 'user', 'content': prompt}],
            stop=self.stop_pattern)

        tool, tool_input = self._parse(generated)
        print('tool', tool)
        print('tool_input', tool_input)
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        if FINAL_ANSWER_TOKEN in generated:
            if self.verbose:
                print('------')
                print('FINAL ANSWER')
                print('------')
                print(generated)
                print('------')
            final_answer = generated.split(FINAL_ANSWER_TOKEN)[-1].strip()
            return "Assistant Response", final_answer
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            raise ValueError(f"Output of LLM is not parsable for next tool use: `{generated}`")
        tool = match.group(1).strip()
        tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')
