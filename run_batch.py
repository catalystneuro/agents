#!/usr/bin/env python3
import os
import subprocess
import multiprocessing  # noqa: F401 - Used when not in mock mode
import argparse
import time
import datetime
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
        "-e=RUN_MODE=script",
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


def create_mock_results():
    """
    Create mock results for testing the analyze_results function
    """
    return [
        {
            "process_num": 1,
            "success": True,
            "exit_code": 0,
            "execution_time": 120.5,
            "files_created": 15
        },
        {
            "process_num": 2,
            "success": True,
            "exit_code": 0,
            "execution_time": 145.2,
            "files_created": 12
        },
        {
            "process_num": 3,
            "success": False,
            "exit_code": 1,
            "execution_time": 60.3,
            "files_created": 3
        },
        {
            "process_num": 4,
            "success": True,
            "exit_code": 0,
            "execution_time": 130.8,
            "files_created": 14
        }
    ]


def analyze_results(results):
    """
    Analyze the results after all containers have finished.
    """
    # Count successful runs
    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print("\nAll containers have completed.")
    print(f"Summary: {successful} of {total} containers completed successfully")
    print("\nPerforming results analysis...")

    # Find all protocol/session combinations
    protocol_sessions = []
    data_dir = Path("data")
    print("\nAnalyzing protocol/session combinations...")

    for protocol_dir in data_dir.iterdir():
        if protocol_dir.is_dir():
            protocol_name = protocol_dir.name
            for session_dir in protocol_dir.iterdir():
                if session_dir.is_dir():
                    session_name = session_dir.name
                    protocol_sessions.append((protocol_name, session_name))
                    print(f"  - Found protocol/session: {protocol_name}/{session_name}")

    # Create markdown content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    markdown_filename = f"results_{timestamp}.md"

    markdown_content = f"""# Container Execution Results

**Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Summary:** {successful} of {total} containers completed successfully

**Total protocol/session combinations:** {len(protocol_sessions)}

## Container Details

| Agent | Status | Duration | Code Files | NWB Files |
|-------|--------|----------|------------|-----------|
"""

    # Analyze outputs from each workspace
    for result in results:
        process_num = result["process_num"]
        workspace_dir = f"agent_workspace/{process_num}"
        status = "✅ Success" if result["success"] else "❌ Failed"

        # Check NWB files
        converted_results_dir = Path(f"agent_workspace/{process_num}/converted_results")
        if not converted_results_dir.exists():
            nwb_file_count = 0
            missing_files = len(protocol_sessions)
            nwb_column = f"{nwb_file_count}/{len(protocol_sessions)} ❌ (directory not found)"
        else:
            nwb_files = list(converted_results_dir.rglob('*.nwb'))
            nwb_file_count = len(nwb_files)
            expected_nwb_files = len(protocol_sessions)
            missing_files = expected_nwb_files - nwb_file_count

            if missing_files == 0:
                nwb_column = f"{nwb_file_count}/{len(protocol_sessions)} ✅"
            else:
                nwb_column = f"{nwb_file_count}/{len(protocol_sessions)} ❌"

        # Add to markdown content
        row = (f"| {process_num} | {status} | {result['execution_time']:.2f} s | "
               f"{result['files_created']} | {nwb_column} |\n")
        markdown_content += row

        # Print to console
        print(f"Processing results from workspace {workspace_dir}...")
        print(f"  - Execution time: {result['execution_time']:.2f} seconds")
        print(f"  - Files created: {result['files_created']}")
        print(f"  - NWB files: {nwb_file_count}/{len(protocol_sessions)} ({missing_files} missing)")

    # Write markdown file
    with open(markdown_filename, "w") as f:
        f.write(markdown_content)

    print(f"\nResults saved to {markdown_filename}")


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

    # with multiprocessing.Pool(processes=args.num_processes) as pool:
    #     process_nums = range(1, args.num_processes + 1)
    #     results = pool.map(run_docker_container, process_nums)

    results = create_mock_results()  # For testing purposes

    # Analyze the results after all containers have finished
    analyze_results(results)

    # Clean up Docker containers
    print("Cleaning up Docker containers...")
    # for process_num in process_nums:
    #     container_name = f"llm-agent-{process_num}"
    #     subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    return 0


if __name__ == "__main__":
    exit(main())
