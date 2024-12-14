concept_prompt = """
Problem Statement:
{statement}

## Sample Test cases for reference:
Input:
{sample_input}
Output:
{sample_output}

Possible Concepts List:
- Number Theory
- Math
- Dynamic Programming
- Games
- Combinatorics
- Greedy
- Data Structures
- Geometry
- Graph Algorithms
- Strings
- Bit Manipulation
- Recursion
- Sorting
- Searching
- Brute Force
- Divide and Conquer
- Two Pointers
- Binary Search
- Hashing
- Stack
- Queue
- Trees
- Heaps
- Segment Trees
- Fenwick Trees
- Implementation


Your Task:
1. Analyze the problem above, and the sample test cases.
2. Brainstorm thoroughly and select which concepts from the above list may be relevant to solve the problem in a string separated by commas.

Output your analysis and concepts in the following JSON format below. DO NOT output anything other than one JSON string. Output all your analysis in a single line.
{{"analysis": <your analysis>, "concepts": <your concepts>}}
"""

concept_retry_prompt = """
Problem Statement:
{statement}

## Sample Test cases for reference:
Input:
{sample_input}
Output:
{sample_output}

Your previous response:
{response}

Your Task:
1. Analyze the problem above, pay attention to the constraints.
2. Analyze your previous response. Are you sure the list of concepts you provided are relevant to solve the problem? If not, brainstorm again to select which concepts from the above list may be relevant to solve the problem in a string separated by commas.

Output your analysis and concepts in the following JSON format below. DO NOT output anything other than one JSON string. Output all your analysis in a single line.
{{"analysis": <your analysis>, "concepts": <your updated concepts>}}
"""