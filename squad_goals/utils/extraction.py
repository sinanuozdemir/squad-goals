import json
import re


def extract_json_from_string(input_string):
    # Use regex to find the JSON part
    match = re.search(r'({.*?})', input_string, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            # Load the JSON string as a dictionary
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    # now use regex to find a dictionary or list that we can eval
    match = re.search(r'([\[{].*?[\]}])', input_string, re.DOTALL)
    if match:
        try:
            # Load the dictionary or list as a dictionary
            return eval(match.group(1))
        except Exception:
            return None
    else:
        return None
