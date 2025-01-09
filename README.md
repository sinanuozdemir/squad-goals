
# Squad Goals

Originally written for a [lecture on Agents for O'Reilly](https://learning.oreilly.com/live-events/ai-agents-a-z/0642572007604/), **Squad Goals** is an educational Python package designed to manage goals, tasks, and agents while integrating with large language models and tools like SerpAPI. The goal here is to show off how simple it can be to make a basic Agent framework.

## Installation

Install `squad-goals` directly from this repository:

```bash
pip install git+https://github.com/sinanuozdemir/squad-goals.git
```

This command installs `squad-goals` along with its dependencies.

## Usage

Here’s a quick example of how to use `squad-goals` with different components:

```python
from squad_goals import Agent, Task
from squad_goals.tools import SerpTool
from squad_goals.llms import OpenAILLM
import os

# Set API keys as environment variables
os.environ['SERP_API_KEY'] = 'your_serp_api_key'
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key'

# Initialize the OpenAI LLM
openai_llm = OpenAILLM(model_name='gpt-4o-mini')

# Initialize the SerpTool for web searching
serp_tool = SerpTool()

# Create an agent with tools and an LLM
agent = Agent(
    tools=[serp_tool],
    llm=openai_llm,
    verbose=False
)

# Define a task with a goal
lookup_task = Task(
    name='Lookup',
    goal='Tell me about Sinan Ozdemir. Only make one web search.',
)

# Run the task with the agent
agent.run(lookup_task)

# Create and run another task with multiple web lookups allowed
wider_lookup_task = Task(
    name='Lookup',
    goal='Tell me about Sinan Ozdemir. Make multiple web lookups.',
)

agent.run(wider_lookup_task)
```

## Features

- **Agent and Task Management**: Define agents with specific tasks and goals.
- **LLM Integration**: Use OpenAI LLMs to process and generate responses.
- **Web Lookup via SerpAPI**: Perform web searches as part of task execution.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for suggestions.

## License

This project is licensed under the MIT License.
