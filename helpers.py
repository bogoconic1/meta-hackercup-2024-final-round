import re, json

initial_prompt = """
You are an expert Python programmer with a top rank on Codeforces (Grandmaster or International Grandmaster level). Your task is to create optimal Python code to solve the given problem, ensuring it can handle large inputs within the time constraints.

Problem Statement:
{statement}

Possible Time Complexity:
{time_complexity}

Possible Concepts:
{concepts}

## Sample Test cases for reference:
Input:
{sample_input}
Output:
{sample_output}

Your Task:
1. Create a python program that returns the correct output for the given input. 
2. Make the code efficient and fast, so we can solve large inputs.

3. The file should have a single `solve` method that has the following signature:
input: str: The Input in the same format provided above
output: str: The Output in the same format provided above

```python
<insert necessary imports>
def solve(input: str) -> str: 
```
"""

error_prompt = """The code execution failed due to an error: {str(e)}. Please fix the code to handle this error.
Current code:
{last_run_code}
Problem description:
{statement}
Sample input:
{sample_input}
Expected output:
{sample_output}

Please think out loud on what went wrong, and provide a corrected version of the code."""

def clean_invalid_escapes(json_string):

    valid_escape_sequences = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r']
    escape_sequence_regex = r'\\.'

    def replace_invalid_escapes(match):
        escape_seq = match.group(0)
        if escape_seq not in valid_escape_sequences:
            return escape_seq[1:]
        return escape_seq

    cleaned_json_string = re.sub(escape_sequence_regex, replace_invalid_escapes, json_string)
    
    return cleaned_json_string

def parse_code(response: str) -> str:
    if "```" not in response:
        return response
    code_pattern = r"```python((.|\n)*?)```"
    code_blocks = re.findall(code_pattern, response, re.DOTALL)
    if code_blocks:
        return code_blocks[-1][0].strip()
    return response

def parse_json(response: str) -> dict:
    try:
        return json.loads(clean_invalid_escapes(response))
    except json.JSONDecodeError as e:
        json_pattern = r"```json((.|\n)*?)```"
        json_blocks = re.findall(json_pattern, response, re.DOTALL)
        response = clean_invalid_escapes(json_blocks[-1][0].strip())
        print(response)
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(e)
            return ""