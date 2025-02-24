import os

os.system('pip install openai')


from dotenv import load_dotenv

from squad_goals import Agent, Task
from squad_goals.llms.openai import OpenAILLM
from squad_goals.tools import SerpTool

# Load environment variables from test.env
load_dotenv("test.env")


def test_agent_execution():
    """Test agent execution with a simple task."""
    assert 'OPENAI_API_KEY' in os.environ, "OPENAI_API_KEY missing from environment."
    assert 'SERP_API_KEY' in os.environ, "SERP_API_KEY missing from environment."

    # Initialize OpenAI LLM
    openai_llm = OpenAILLM(model_name='gpt-4o-mini')
    serp_tool = SerpTool(api_key=os.environ.get('SERP_API_KEY'))

    # Create the agent
    agent = Agent(
        llm=openai_llm,
        tools=[serp_tool],
        max_loops=3,
        verbose=True
    )

    # Define a task
    task = Task(
        name="Test Task",
        goal="Tell me about Sinan Ozdemir."
    )

    events = list(agent.run(task, yield_events=True))

    assert any(event['event'] == 'agent_completed' for event in events), "Agent did not complete the task."
