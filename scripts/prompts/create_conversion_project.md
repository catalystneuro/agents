Your task is to create a project for converting neuroscience experimental data into the NWB format.

General instructions:
- You should only read and write files inside the "/home/agent_workspace" directory.
- The first thing you must do is to create an NWB conversion repository using the create_nwb_repo tool, inside your working directory.
- All the code files you produce must be saved inside this created project folder.
- Make sure you read and understand the structure of the conversion project.
- The conversion should be done using Neuroconv. Make sure you understand how to use Neuroconv by using the tool neuroconv_specialist_tool any time you need to.
- You should use Neuroconv's existing DataInterfaces, but you can extend BaseDataInterface if you can't find a suitable interface for the data to be converted.
- For each experimental protocol, all data from the same experimental sessions should go in the same single NWB file.

Test and validation:
- Your goal is to convert the data from the provided experimental protocols into NWB files, using the tools you wrote in the conversion project.
- You must always run the conversion process by executing "python run_conversion.py" using the execute_command tool.
- You must always ensure the NWB files are correctly formatted and contain all necessary data.
- You must always inspect the NWB files using the inspect_nwb_files tool. Iterate and make corrections on your conversion scripts until the NWB files are correctly formatted and passing all inspection tests.

Project specifics:
- lab name: Tauffer lab

protocol00:
- name: tauffer2025
- description: I have performed experimental recordings of mice free roaming through a maze
- associated publications: None
- data:
-- raw electrophysiology data: spikeglx recordings. Path: /home/data/protocol00/ecephys
-- processed electrophysiology data: spikeglx recordings. Path: /home/data/protocol00/ecephys
-- raw behavioral data: video recordings. Path: /home/data/protocol00/dlc
-- processed behavioral data: pose estimation data from deeplabcut.  Path: /home/data/protocol00/dlc