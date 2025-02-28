import json
import re

def extract_json_from_string(input_string):
    # Use regex to find the JSON part
    # input_string = re.sub(r'[\x00-\x1F\x7F]', '', input_string)  # Remove control characters

    # Try to find JSON objects with curly braces
    matches = re.findall(r'({(?:[^{}]|(?:{[^{}]*}))*})', input_string, re.DOTALL)
    for match in matches:
        try:
            # Load the JSON string
            return json.loads(match, strict=False)
        except Exception:
            pass

    # Try to find JSON objects with balanced braces/brackets
    matches = re.findall(r'(\{(?:[^{}]|(?:\{[^{}]*\}))*\}|\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\])', input_string, re.DOTALL)
    for match in matches:
        try:
            match = match.replace('\\"', '"')
            return eval(match)
        except Exception:
            pass
    
    # Try to find arrays or simple objects that can be evaluated
    matches = re.findall(r'([\[{].*?[\]}])', input_string, re.DOTALL)
    for match in matches:
        try:
            match = match.replace('\\"', '"')
            return eval(match)
        except Exception:
            pass

    return None
