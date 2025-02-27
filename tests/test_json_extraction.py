import unittest
from squad_goals.utils.extraction import extract_json_from_string


class TestExtraction(unittest.TestCase):
    def assertIsJson(self, _input):
        self.assertTrue(isinstance(_input, dict) or isinstance(_input, list))

    def test_valid_json(self):
        input_string = "Some text {\"key\": \"value\"} more text"
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_invalid_json(self):
        input_string = "Some text {\"key\": \"value\" more text"
        self.assertIsNone(extract_json_from_string(input_string), "Invalid JSON should return None.")

    def test_no_json(self):
        input_string = "Some text without json"
        self.assertIsNone(extract_json_from_string(input_string), "No JSON should return None.")

    def test_nested_json(self):
        input_string = "Some text {\"key\": {\"nested_key\": \"nested_value\"}} more text"
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_list_json(self):
        input_string = "Some text [1, 2, 3] more text"
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_long_json(self):
        input_string = """Thought: I need to gather financial information about the company. 

Action: Return Final Answer Tool
Action Input: {\"final_answer\": [\"Identify the relevant financial statements (e.g., income statement, balance sheet, cash flow statement) for <<company_name>> over the past year.\", \"Analyze key financial metrics such as revenue, profitability, liquidity, and debt levels.\", \"Compare the company's financial performance to its historical trends and industry benchmarks.\", \"Identify any significant financial events or developments during the year.\", \"Summarize the overall financial health and performance of <<company_name>>. \"]} 
 
"""
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_long_json_two(self):
        input_string = """Thought: I need to figure out how to find well-regarded Italian restaurants 

Action: Return Final Answer Tool
Action Input: {"final_answer": [\"Use a restaurant rating platform (like Yelp or Google Maps) to search for Italian restaurants in New York City\",\"Filter the results by rating, location, and cuisine type\",\"Read reviews from multiple sources to get a well-rounded view of each restaurant\",\"Consider factors like ambiance, price range, and menu offerings\",\"Make a selection based on your preferences and desired dining experience\"]}

"""
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_eval_json_two(self):
        input_string = '"[\\"Gather the financial statements of <<company_name>> for the past year\\", \\"Analyze the revenue and expenses of <<company_name>> over the past year\\", \\"Calculate key financial metrics such as profit margin and return on investment\\", \\"Compare the financial performance of <<company_name>> to industry averages\\", \\"Summarize the findings in a comprehensive report\\"]"'
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

    def test_eval_json_three(self):
        input_string = "[\"Define the target audience and unique selling points of the smartphone app\", \"Conduct market research on similar apps and identify the competitive landscape\", \"Develop a content marketing strategy, including social media and advertising channels\", \"Create a budget and timeline for the marketing plan\", \"Monitor and evaluate the performance of the marketing plan and make adjustments as needed\"]"
        result = extract_json_from_string(input_string)
        self.assertIsJson(result)

if __name__ == "__main__":
    unittest.main() 