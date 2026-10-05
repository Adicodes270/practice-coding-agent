import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from functions.call_function import call_function


def main():

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

        - List files and directories
        - Read the content of a file
        - Write content to a file (creating it and any missing folders, or overwriting it)
        - Run a Python file with optional command-line arguments


        All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
        """
    model = os.getenv("GEMINI_MODEL")

    prompt = input("Enter the prompt: ")
    verbose = input("Verbose? (y/n): ").strip().lower() == "y"

    message = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    available_functions = types.Tool(
        function_declarations = [

            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file,
        ]
    )

    max_iters = 20
    for i in range(0, max_iters):
        response = client.models.generate_content(
            model=model,
            contents=message,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        if response is None or response.usage_metadata is None:
            print("Response is malformed or missing usage metadata.")
            return

        if verbose:
            print(f"User prompt: {prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None:
                    continue
                message.append(candidate.content)
        

        if response.function_calls:
            for function_call_part in response.function_calls:
        
                result = call_function(function_call_part , verbose=verbose)
                message.append(result)
        else:
            """ Final agent text message """
            print(response.text)
            return


main()