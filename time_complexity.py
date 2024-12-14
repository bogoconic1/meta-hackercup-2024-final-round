tc_prompt = """
Time Complexity Guide:

Let n be the main variable in the problem.
Maximum allowed Time Complexity Guidelines:
n ≤ 12: O(n!)
n ≤ 25: O(2^n)
n ≤ 100: O(n^4)
n ≤ 500: O(n^3)
n ≤ 10^4: O(n^2)
n ≤ 10^6: O(n log n)
n ≤ 10^8: O(n)
n > 10^8: O(log n) or O(1)

Examples:
O(n!): Permutations
O(2^n): Subset exhaustion
O(n^3): Triangle enumeration
O(n^2): Slow sorting (Bubble, Insertion, Selection)
O(n log n): Fast sorting (Merge Sort)
O(n): Linear Search, Counting Sort
O(log n): Binary Search, Euclidean GCD
O(1): Simple calculations

Problem Statement:
{statement}

## Sample Test cases for reference:
Input:
{sample_input}
Output:
{sample_output}

Your Task:
1. Analyze the problem above, pay attention to the constraints.
2. Use the time complexity guide provided above to derive the complexity of an algorithm that is fast enough to execute given the problem constraints. Do not solve the problem, just brainstorm on the time complexity given the problem constraints.

Output your analysis and time complexity in the following JSON format below. DO NOT output anything other than one JSON string. Output all your analysis in a single line.
{{"analysis": <your analysis>, "time_complexity": <your time complexity>}}
"""

tc_retry_prompt = """
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
2. Analyze your previous response. Are you sure it is fast enough to execute given the problem constraints? If not, think of enhancements to the algorithm to reduce the time complexity.

Output your analysis and time complexity in the following JSON format below. DO NOT output anything other than one JSON string. Output all your analysis in a single line.
{{"analysis": <your analysis>, "time_complexity": <your updated time complexity>}}
"""