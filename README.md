# Squad Goals ![Test Status](https://github.com/sinanuozdemir/squad-goals/actions/workflows/run_tests.yml/badge.svg)

**Squad Goals** is an educational Python package for managing goals, tasks, and agents, integrating with large language models and tools like SerpAPI. Originally developed for a [lecture on Agents for O'Reilly](https://learning.oreilly.com/live-events/ai-agents-a-z/0642572007604/), it demonstrates how to create a basic Agent framework.

## Installation

Install directly from the repository:

```bash
pip install git+https://github.com/sinanuozdemir/squad-goals.git
```

## Usage

Here's a quick example of using `squad-goals`:

```python
from squad_goals import Agent, Task
from squad_goals.tools import SerpTool
from squad_goals.llms.openai import OpenAILLM
import os

# Set API keys
os.environ['SERP_API_KEY'] = 'your_serp_key'
os.environ['OPENAI_API_KEY'] = 'your_openai_key'

# Initialize components
openai_llm = OpenAILLM(model_name='gpt-4o-mini')
serp_tool = SerpTool()
agent = Agent(tools=[serp_tool], llm=openai_llm, verbose=False)

# Define and run tasks
lookup_task = Task(name='Lookup', goal='Tell me about Sinan Ozdemir. Only make one web search.')
events = agent.run(lookup_task)
print(events[-1])

wider_lookup_task = Task(name='Lookup', goal='Tell me about Sinan Ozdemir. Make multiple web lookups.')
events = agent.run(wider_lookup_task)
print(events[-1])
```

More examples are available [here](./example_notebooks).

## Features

- **Agent and Task Management**: Define agents with specific tasks and goals.
- **LLM Integration**: Use OpenAI LLMs to process and generate responses.
- **Web Lookup via SerpAPI**: Perform web searches as part of task execution.

## Contributing

Contributions are welcome! Submit a pull request or open an issue for suggestions.

## License

This project is licensed under the MIT License.

## Running Tests

Ensure functionality by running tests with the sample YAML configuration:

```yaml
verbose: true

// all tasks will use the same agent (same llm, tools, max_loops, etc.)
llm:
  model_name: "claude-3-5-haiku-latest"
  class: "AnthropicLLM"
max_loops: 3
env_vars:
  ANTHROPIC_API_KEY: "***"
  SERP_API_KEY: "***"
tools:
  - SerpTool

tasks:
  - name: "Json Output 1"
    goal: "Write a list of the planets in our solar system as a python list."
    output_format: "json"
    output_length_range: [8, 8]
    check_format: "json"
    // If you don't care about the tool calls, you can omit the tool_calls key.
    tool_calls: [] // this means that you expect no tool calls for this task.
  - name: "Text Output 1"
    goal: "Look up Sinan Ozdemir the AI guy and describe him in 20 words or less."
    word_count_range: [0, 20]
    tool_calls: ["SerpAPI Tool"]
```

### Running the Test

Execute the test script:

- Assumes that `sample_test.yaml` is in the `tests` directory. You can find an example of this file in the `tests` directory. Note the keys in the yaml file are fake.

```bash
python tests/test_agent_from_yaml.py tests/sample_test.yaml
```

### System Tests

For comprehensive system testing, use `./run_tests.sh`
