import os 
import subprocess 
from google.genai import types

def run_python_file(working_directory: str, file_path: str , args = []):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if os.path.commonpath([abs_working_dir, abs_file_path]) != abs_working_dir:
        return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        return f'Error: "{file_path}" is not a file'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    try:
        final_args = ['python3' , file_path]
        final_args.extend(args)

        output = subprocess.run(final_args , cwd=abs_working_dir, timeout=30, capture_output=True)
        final_string =  f'''
        
STDOUT: {output.stdout}
STDERR: {output.stderr}
        
        '''

        if output.stdout == "" and output.stderr == "":
            final_string = "No output from the script \n"


        if output.returncode != 0:
            final_string = f"Process exited with code {output.returncode}"

        return final_string
        

    except Exception as e:
        return f"Error executing file '{file_path}': {e}"


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file with optional command-line arguments, relative to the working directory, and returns its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of command-line arguments to pass to the script",
            ),
        },
        required=["file_path"],
    ),
)