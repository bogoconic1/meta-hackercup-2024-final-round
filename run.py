import asyncio
from dataclasses import dataclass
from pathlib import Path
import logging
import re
import aiofiles  # Asynchronous file operations
import os
from openai import AsyncOpenAI  # Import from AsyncOpenAI library
import weave
import simple_parsing
from argparse import ArgumentParser
from mini_lib.problem import Problem
from mini_lib.utils import maybe_remove_backticks, check_solution, setup_logger, run, arun
from typing import List

#modules
import helpers, time_complexity, wrong_answer, tle, concepts

import nest_asyncio
nest_asyncio.apply()

from dotenv import load_dotenv
load_dotenv()
openai_key = os.environ["OPENAI_API_KEY"]

# Initialize the AsyncOpenAI client
client = AsyncOpenAI(api_key=openai_key)

# Asynchronous version of call_model function
async def call_model(messages, model="o1-mini-2024-09-12", **kwargs):
    print(model)
    response = await client.chat.completions.create(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content

async def get_ac(model: str, problem: Problem, timeout: int, num_tries: int, num_time_complexity_tries: int = 2, num_concepts_tries: int = 2):
    last_run_code, generated_output = None, None

    for i in range(num_tries):
        logging.info(f"Attempt {i+1}/{num_tries}")

        if i == 0:
            logging.info("Time Complexity Attempt 1")
            prompt = time_complexity.tc_prompt.format(
                statement=problem.problem_description,
                sample_input=problem.sample_input,
                sample_output=problem.sample_output,
            )
            logging.info(prompt)
            messages = [{"role": "user", "content": prompt}]
            response = await call_model(messages=messages, model=model)
            logging.info(response)
            problem_time_complexity = helpers.parse_json(response)["time_complexity"]
            time_complexity_tries = 1
            
            while time_complexity_tries < num_time_complexity_tries:
                logging.info(f"Time Complexity Attempt {time_complexity_tries + 1}")
                prompt = time_complexity.tc_retry_prompt.format(
                    response=problem_time_complexity,
                    statement=problem.problem_description,
                    sample_input=problem.sample_input,
                    sample_output=problem.sample_output,
                )
                logging.info(prompt)
                messages = [{"role": "user", "content": prompt}]
                response = await call_model(messages=messages, model=model)
                logging.info(response)
                problem_time_complexity = helpers.parse_json(response)["time_complexity"]
                time_complexity_tries += 1

            logging.info("Concepts Attempt 1")
            prompt = concepts.concept_prompt.format(
                statement=problem.problem_description,
                sample_input=problem.sample_input,
                sample_output=problem.sample_output,
            )
            logging.info(prompt)
            messages = [{"role": "user", "content": prompt}]
            response = await call_model(messages=messages, model=model)
            logging.info(response)
            problem_concepts = helpers.parse_json(response)["concepts"]
            concepts_tries = 1

            while concepts_tries < num_concepts_tries:
                logging.info(f"Concepts Attempt {concepts_tries + 1}")
                prompt = concepts.concept_retry_prompt.format(
                    response=problem_concepts,
                    statement=problem.problem_description,
                    sample_input=problem.sample_input,
                    sample_output=problem.sample_output,
                )
                logging.info(prompt)
                messages = [{"role": "user", "content": prompt}]
                response = await call_model(messages=messages, model=model)
                logging.info(response)
                problem_concepts = helpers.parse_json(response)["concepts"]
                concepts_tries += 1

            try:
                prompt = helpers.initial_prompt.format(
                    time_complexity=problem_time_complexity,
                    concepts=problem_concepts,
                    statement=problem.problem_description,
                    sample_input=problem.sample_input,
                    sample_output=problem.sample_output,
                )
                logging.info(prompt)
                messages = [{"role": "user", "content": prompt}]
                response = await call_model(messages=messages, model=model)
                last_run_code = helpers.parse_code(response)
                logging.info(response)

                try:
                    generated_output = await arun(code=last_run_code, input=problem.sample_input, timeout=timeout)
                except TimeoutError:
                    logging.warning(f"Timeout occurred while solving problem: {problem.name}. Moving to next problem.")
                    return  # Stop further attempts and move on to the next problem
            except Exception as e:
                error_prompt = f"""The code execution failed due to an error: {str(e)}. Please fix the code to handle this error.
                                    Current code:
                                    {last_run_code}
                                    Problem description:
                                    {problem.problem_description}
                                    Sample input:
                                    {problem.sample_input}
                                    Expected output:
                                    {problem.sample_output}

                                    Please think out loud on what went wrong, and provide a corrected version of the code."""

                messages = [{"role": "user", "content": error_prompt}]
                response = await call_model(messages=messages, model=model)
                last_run_code = helpers.parse_code(response).replace("sys.stdin.read", "sys.stdin.read()")
                logging.info(response)
                generated_output = await arun(last_run_code, input=problem.sample_input, timeout=timeout)

        else:
            try:
                prompt = tle.tle_prompt.format(
                    time_complexity=problem_time_complexity,
                    concepts=problem_concepts,
                    statement=problem.problem_description,
                    code=last_run_code,
                )
                logging.info(prompt)
                messages = [{"role": "user", "content": prompt}]
                response = await call_model(messages=messages, model=model)
                corrected_code = helpers.parse_code(response)
                logging.info(response)
                generated_output = await arun(corrected_code, input=problem.sample_input, timeout=timeout)
            except Exception as e:
                error_prompt = f"""The code execution failed due to an error: {str(e)}. Please fix the code to handle this error.
                                    Current code:
                                    {corrected_code}
                                    Problem description:
                                    {problem.problem_description}
                                    Sample input:
                                    {problem.sample_input}
                                    Expected output:
                                    {problem.sample_output}

                                    Please think out loud on what went wrong, and provide a corrected version of the code."""

                messages = [{"role": "user", "content": error_prompt}]
                response = await call_model(messages=messages, model='gpt-4o-2024-11-20')
                corrected_code = helpers.parse_code(response).replace("sys.stdin.read", "sys.stdin.read()")
                logging.info(response)
                generated_output = await arun(corrected_code, input=problem.sample_input, timeout=timeout)

            try:
                prompt = wrong_answer.wa_prompt.format(
                    time_complexity=problem_time_complexity,
                    concepts=problem_concepts,
                    statement=problem.problem_description,
                    code=corrected_code,
                    sample_input=problem.sample_input,
                    sample_output=problem.sample_output,
                    code_output=generated_output,
                )
                logging.info(prompt)
                messages = [{"role": "user", "content": prompt}]
                response = await call_model(messages=messages, model=model)
                corrected_code = helpers.parse_code(response)
                logging.info(response)
                generated_output = await arun(corrected_code, input=problem.sample_input, timeout=timeout)
            except Exception as e:
                error_prompt = f"""The code execution failed due to an error: {str(e)}. Please fix the code to handle this error.
                                    Current code:
                                    {corrected_code}
                                    Problem description:
                                    {problem.problem_description}
                                    Sample input:
                                    {problem.sample_input}
                                    Expected output:
                                    {problem.sample_output}

                                    Please think out loud on what went wrong, and provide a corrected version of the code."""

                messages = [{"role": "user", "content": error_prompt}]
                response = await call_model(messages=messages, model='gpt-4o-2024-11-20')
                corrected_code = helpers.parse_code(response).replace("sys.stdin.read", "sys.stdin.read()")
                logging.info(response)
                generated_output = await arun(corrected_code, input=problem.sample_input, timeout=timeout)

            if corrected_code == last_run_code:
                break

            last_run_code = corrected_code

        if len(generated_output) == 0:
            logging.warning("Empty output generated. Threading detected...")
            break


    # Use aiofiles for asynchronous file operations
    async with aiofiles.open(f'output/{model}/{problem.name}_code.py', 'w', encoding='utf-8') as fout:
        await fout.write(last_run_code)

    logging.info("> Solving on full input...")
    sample_output = await arun(last_run_code, input=problem.sample_input, timeout=timeout)
    generated_output = await arun(last_run_code, input=problem.get_input(), timeout=timeout)

    logging.debug(f"Sample output: {sample_output}")
    logging.debug(f"Generated output: {generated_output}")

    async with aiofiles.open(f"output/{model}/{problem.name}_sample_output.txt", "w", encoding='utf-8') as f:
        await f.write(sample_output)

    async with aiofiles.open(f"output/{model}/{problem.name}_output.txt", "w", encoding='utf-8') as f:
        await f.write(generated_output)

@dataclass
class Args(simple_parsing.Serializable):
    folder_path: Path = Path("problems") 
    weave_log: bool = False
    use_images: bool = False
    save_output: bool = True
    debug: bool = False
    timeout: int = 10
    max_attempts: int = 2
    num_time_complexity_tries: int = 4
    num_concepts_tries: int = 2
    model: str = "o1-mini-2024-09-12"
    problem_name: str = ""

async def main():
    args = simple_parsing.parse(Args)
    setup_logger(args.debug)

    problems = [
        args.problem_name.lstrip("'").rstrip("'")
    ]
    
    tasks = []
    for problem_name in problems:
        problem = Problem.from_name(problem_name, args.folder_path / f"{problem_name}")
        if args.weave_log:
            weave.init("hack-starter")
        tasks.append(get_ac(model=args.model, 
                            problem=problem, 
                            timeout=args.timeout, 
                            num_tries=args.max_attempts, 
                            num_time_complexity_tries=args.num_time_complexity_tries, 
                            num_concepts_tries=args.num_concepts_tries))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())