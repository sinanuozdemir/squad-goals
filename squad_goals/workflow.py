import re
from typing import List, Any, Dict

from pydantic import BaseModel

from squad_goals.tools.base_tool import BaseTool
from .task import Task


class Plan(BaseModel):
    goal: str
    steps: List[str]
    results: List[str] = []

    @property
    def is_complete(self) -> bool:
        return len(self.steps) == len(self.results)

    def formatted_plan(self, include_goal=True) -> str:
        ''' return the plan as a formatted string including the goal and steps '''
        if include_goal:
            return f'Goal: {self.goal}\n' + '\n'.join(
                [f'{step} -> {result}' for step, result in zip(self.steps, self.results) if result])
        else:
            return '\n'.join([f'{step} -> {result}' for step, result in zip(self.steps, self.results) if result])


class Workflow(BaseModel):
    plan: Plan
    goal: str
    agent: Any  # TODO eventually multi agents here
    tasks: List[Any] = []
    verbose: bool = False

    def _extract_variables(self, text):
        ''' find <<x>> variables in the goal and return them as a list '''
        return re.findall(r'<<([^>]*)>>', text)

    def _replace_variables(self, text, **values: Dict[str, str]):
        ''' replace <<x>> variables in the goal with the values '''
        for variable, value in values.items():
            if f'<<{variable}>>' in text:
                text = text.replace(f'<<{variable}>>', value)

        if '<<' in text:
            raise ValueError(f"At least one variable was not replaced in the text: {text}")
        return text

    def run(self, **variables: Dict[str, str]):
        ''' run the workflow '''
        self.plan.results = []  # reset results
        while not self.plan.is_complete:
            # create plan_formatted which is the list of steps with results if they exist

            next_step = self.plan.steps[len(self.plan.results)]
            next_step = self._replace_variables(next_step, **variables)
            if self.verbose:
                print(f"Next Step: {next_step}")

            on_last_step = len(self.plan.results) == (len(self.plan.steps) - 1)
            plan_formatted = self.plan.formatted_plan(include_goal=on_last_step)
            plan_formatted = self._replace_variables(plan_formatted, **variables)
            if self.verbose:
                print(f"Formatted Plan: {plan_formatted}")

            step_task = Task(
                name=f"Execute Step {len(self.plan.results) + 1}",
                goal=f'You are executing a SINGLE step of the following plan.\n\n<plan>\n{plan_formatted}\n</plan>\n\nThe step you are now executing is:\n\n<step>\n{next_step}\n</step>\n\nExecute only the given step of the plan and nothing more.',
                output_format='text'
            )
            self.tasks.append(step_task)
            self.agent.run(step_task)
            step_result = step_task.output
            self.plan.results.append(step_result)
            if self.verbose:
                print(f"Step Result: {step_result}")

        return self.plan.results


class WorkflowTool(BaseTool):

    def __init__(self, workflow: Workflow, verbose: bool = False, **kwargs):
        self.workflow = workflow
        self.verbose = verbose
        kwargs.update(
            {
                'name': workflow.goal,
                'description': f"Runs a workflow with the following plan: {workflow.plan.formatted_plan()}"
            }
        )
        super().__init__(**kwargs)

    def run(self, **variables: Dict[str, str]):
        variables.update({'verbose': self.verbose})
        results = self.workflow.run(**variables)
        return results[-1]

    # base tool has _describe_run, but add the workflow variables here so they know to set it
    def _describe_run(self):
        workflow_variables = self.workflow._extract_variables(self.workflow.goal)
        return 'Parameters to include in Action Input dictionary:\n' + '\n'.join(
            [f'\t{variable}: {variable} as a string' for variable in workflow_variables])
