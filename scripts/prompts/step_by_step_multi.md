Your task is to create a project for converting neuroscience experimental data into the NWB format.

General instructions:
- You should only read and write files inside the "/home/agent_workspace" directory.
- the nwb_conversion_specialist_agent will be responsible for the conversion process, including writing the code and running the conversion of the original data to nwb
- the nwb_inspector_agent will be responsible for inspecting the nwb files and validating them, and should always work right after the nwb_conversion_specialist_agent finishes the conversion
- the manager_agent will coordinate the workflow between the other agents, and should relegate the tasks to the specialist agents in the correct order

Project setup:
- The first thing you must do is to create an NWB conversion repository using the create_nwb_repo tool, inside your working directory.
- Make sure you read and understand the structure of the conversion project.
- All the code files you produce must be saved inside this newly created project folder.

Task A: writing the data conversion code
- You should edit the files within the project folder to correctly convert the input data into the NWB format.
- The conversion should be done using Neuroconv. Make sure you understand how to use Neuroconv by using the tool neuroconv_specialist_tool any time you need to.
- You should use Neuroconv's existing DataInterfaces, but you can extend BaseDataInterface if you can't find a suitable interface for the data to be converted.
- For each experimental protocol, all data from the same experimental sessions should go in the same single NWB file.
- Ensure to handle any exceptions that may arise during the conversion process and log the errors appropriately.
- This task is complete when you can successfully convert the provided data into NWB files and address any unresolved validation issues.

Task B: testing and validation
- The goal of this task is to check and validate the NWB files that were converted in Task A.
- Use the "inspect_nwb_files" tool to validate the NWB files.
- Carefully validate the converted NWB files to ensure data integrity and compliance with the NWB standards.
- Document any encountered issues during the validation process.
- Finish the task when all files were tested.

Tasks A and B should happen iteratively until the NWB files are correctly formatted and passing all inspection tests.

Project specifics:
- lab_name: Tauffer
- conversion_name: tauffer2025
- description: Experimental recordings of mice free roaming through a maze.
- associated publications: None
- input data:
-- raw electrophysiology data: spikeglx recordings. Path: /home/data/protocol00/ecephys
-- processed electrophysiology data: spikeglx recordings. Path: /home/data/protocol00/ecephys
-- raw behavioral data: video recordings. Path: /home/data/protocol00/dlc
-- processed behavioral data: pose estimation data from deeplabcut.  Path: /home/data/protocol00/dlc