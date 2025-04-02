#!/usr/bin/env python3
import os
import subprocess
import multiprocessing
import argparse
import time
from pathlib import Path


def count_files_in_directory(directory):
    """
    Count the number of files in a directory and its subdirectories
    """
    count = 0
    for path in Path(directory).rglob('*'):
        if path.is_file():
            count += 1
    return count


def run_docker_container(process_num):
    """
    Run a Docker container with process-specific agent workspace and wait for completion
    """
    # Create process-specific agent workspace directory if it doesn't exist
    workspace_dir = Path(f"agent_workspace/{process_num}")
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # Count files before starting (to calculate new files later)
    initial_file_count = count_files_in_directory(workspace_dir)

    # Container name with process number to make it unique
    container_name = f"llm-agent-{process_num}"

    # Build the docker run command (without -d flag for non-detached mode)
    cmd = [
        "docker", "run",
        f"--name={container_name}",
        # Environment variables
        f"-e=OPENROUTER_API_KEY={os.environ.get('OPENROUTER_API_KEY', '')}",
        f"-e=OPENAI_API_KEY={os.environ.get('OPENAI_API_KEY', '')}",
        f"-e=QDRANT_API_KEY={os.environ.get('QDRANT_API_KEY', '')}",
        f"-e=TELEMETRY_ENABLED={os.environ.get('TELEMETRY_ENABLED', 'false')}",
        # Volume mounts
        f"-v={os.path.abspath('data')}:/home/data",
        f"-v={os.path.abspath('scripts')}:/home/scripts",
        f"-v={os.path.abspath(f'agent_workspace/{process_num}')}:/home/agent_workspace",
        # Image name
        "catalystneuro_agent"
    ]

    print(f"Starting container {container_name} with workspace agent_workspace/{process_num}")

    # Record start time
    start_time = time.time()

    # Run the container
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Calculate execution time
    execution_time = time.time() - start_time

    exit_code = result.returncode
    if exit_code != 0:
        print(f"Container {container_name} exited with error code {exit_code}: {result.stderr}")
    else:
        print(f"Container {container_name} completed successfully")

    # Count files after completion
    final_file_count = count_files_in_directory(workspace_dir)
    files_created = final_file_count - initial_file_count

    return {
        "process_num": process_num,
        "success": exit_code == 0,
        "exit_code": exit_code,
        "execution_time": execution_time,
        "files_created": files_created
    }


def process_results(results):
    """
    Process the results after all containers have finished
    """
    # Count successful runs
    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print("\nAll containers have completed.")
    print(f"Summary: {successful} of {total} containers completed successfully")
    print("\nPerforming results analysis...")

    # Analyze outputs from each workspace
    for result in results:
        process_num = result["process_num"]
        workspace_dir = f"agent_workspace/{process_num}"
        print(f"Processing results from workspace {workspace_dir}...")
        print(f"  - Execution time: {result['execution_time']:.2f} seconds")
        print(f"  - Files created: {result['files_created']}")


def main():
    parser = argparse.ArgumentParser(description='Run multiple LLM agent containers in parallel')
    parser.add_argument(
        '-n',
        '--num-processes',
        type=int,
        default=4,
        help='Number of parallel processes to run (default: 4)',
    )
    args = parser.parse_args()

    # Check if required environment variables are set
    required_vars = ['OPENROUTER_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: The following required environment variables are not set: {', '.join(missing_vars)}")
        print("Please set them before running this script.")
        return 1

    # Create base agent_workspace directory if it doesn't exist
    Path("agent_workspace").mkdir(exist_ok=True)

    # Create and start the processes
    print(f"Starting {args.num_processes} agent containers...")

    with multiprocessing.Pool(processes=args.num_processes) as pool:
        process_nums = range(1, args.num_processes + 1)
        results = pool.map(run_docker_container, process_nums)

    # Process the results after all containers have finished
    process_results(results)

    return 0


if __name__ == "__main__":
    exit(main())
