import yaml
import os
import importlib
from tqdm import tqdm
import logging

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def create_test_agent(llm_config, env_vars, tool_names, verbose):
    # Set API keys as environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Dynamically import the LLM module based on the class name
    if 'anthropic' in llm_config['class'].lower():
        llm_module = importlib.import_module('squad_goals.llms.anthropic')
    elif 'groq' in llm_config['class'].lower():
        llm_module = importlib.import_module('squad_goals.llms.groq')
    else:
        llm_module = importlib.import_module('squad_goals.llms.openai')
    LLMClass = getattr(llm_module, llm_config['class'])
    
    # Initialize the LLM
    llm = LLMClass(model_name=llm_config['model_name'])
    
    # Initialize tools dynamically based on tool names
    tools_module = importlib.import_module('squad_goals.tools')
    tools = []
    for tool_name in tool_names:
        ToolClass = getattr(tools_module, tool_name)
        tools.append(ToolClass())
    
    # Create an agent with tools and an LLM
    agent_module = importlib.import_module('squad_goals')
    Agent = agent_module.Agent
    agent = Agent(
        tools=tools,
        llm=llm,
        verbose=verbose
    )
    return agent

def run_test(logger,task, agent):
    test_passed = True
    # Create a Task object dynamically from the task dictionary
    task_module = importlib.import_module('squad_goals')
    Task = task_module.Task
    task_obj = Task(
        name=task['name'],
        goal=task['goal'],
        output_format=task.get('output_format', 'text'),
    )
    
    # Run the task with the agent
    events = agent.run(task_obj)
    output = task_obj.output
    if not output:
        test_passed = False
        logger.info(f"Output for task '{task_obj.name}' is empty.")
        return events, task_obj, test_passed
    
    # Check if the output is a list or dict and validate JSON format
    check_format = task.get('check_format', 'text')
    if check_format == 'json':
        if not isinstance(output, (list, dict)):
            test_passed = False
            logger.info(f"Output for task '{task_obj.name}' is not valid JSON.")
        if 'output_length_range' in task:
            min_length, max_length = task['output_length_range']
            if len(output) < min_length or len(output) > max_length:
                test_passed = False
                logger.info(f"Output for task '{task_obj.name}' is not within the specified length range.")
    elif check_format == 'text':
        if 'word_count_range' in task:
            min_words, max_words = task['word_count_range']
            word_count = len(output.split())
            if word_count < min_words or word_count > max_words:
                test_passed = False
                logger.info(f"Output for task '{task_obj.name}' has {word_count} words, which is not within the specified range.")
        elif 'char_count_range' in task:
            min_chars, max_chars = task['char_count_range']
            char_count = len(output)
            if char_count < min_chars or char_count > max_chars:
                test_passed = False
                logger.info(f"Output for task '{task_obj.name}' has {char_count} characters, which is not within the specified range.")
    
    
    return events, task_obj, test_passed

def setup_logging(verbose=False):
    # Create a logger
    logger = logging.getLogger(__name__)
    
    # Set the logging level based on the verbose flag
    if verbose:
        logger.setLevel(logging.INFO)
    
    # Create a console handler
    ch = logging.StreamHandler()
    
    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(ch)
    
    return logger

def main():
    config = load_yaml('tests/sample_test.yaml')
    
    # Set up logging
    verbose = config.get('verbose', False)
    logger = setup_logging(verbose)
    
    # Create LLM and agent
    agent = create_test_agent(config['llm'], config['env_vars'], config['tools'], config['verbose'])
    
    passed_tests_count = 0  # Initialize counter for passed tests
    
    # Run tests with a progress bar
    for task in tqdm(config['tasks'], desc="Running tasks"):
        events, task_obj, test_passed = run_test(logger,task, agent)
        passed_tests_count += test_passed
        
        # Log events
        logger.debug(f"Task: {task_obj.name}, Events: {events}")
        
        if config['verbose']:
            if test_passed:
                logger.info(f"Task '{task_obj.name}' passed. ✔")
            else:
                logger.info(f"Task '{task_obj.name}' failed. ❌")
    
    # Display the number of passed tests
    logger.info(f"Number of tests passed: {passed_tests_count} ✔. Number of tests failed: {len(config['tasks']) - passed_tests_count} ❌.")

if __name__ == "__main__":
    main() 