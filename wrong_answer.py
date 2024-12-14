wa_prompt = """
You are given a problem statement, together with a code that someone has written to solve the problem.

Problem Statement:
{statement}

Possible Time Complexity:
{time_complexity}

Possible Concepts:
{concepts}

Code:
{code}

## Sample Test cases for reference:
Sample Input:
{sample_input}
Sample Output:
{sample_output}

Code Output:
{code_output}

Your Task:
1. Analyze the "Sample Output" and "Code Output".
2. Do you think the code is correct? 
3. If your answer to (2) is NO, think of an alternative approach that solves the issue with the code you identified in (2).
4. Ask yourself, does your new approach has equal or lower time complexity than the existing solution ?
5. If your answer to (2) is YES or (4) is NO, code the exact same program that was given. Else, implement the code for the new approach in the `solve` method below.

```python
<insert necessary imports>
def solve(input: str) -> str: 
```
"""