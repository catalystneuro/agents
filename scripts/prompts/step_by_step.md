Your goal is to successfully convert a provided neurophysiology dataset into the NWB format. The process is divided into four main tasks:

1. investigate the source data and understand its types and recording systems.
2. create a project for converting neuroscience experimental data into the NWB format.
3. write the data conversion code and run the conversion process.
4. test and validate the converted NWB files.

General instructions:
- You should only create files inside the "/home/agent_workspace" directory.
- The source data is located in the "/home/data" directory.

Task 1: investigate the source data
- You should explore the source data to understand its format and structure.
- Each folder inside "/home/data" corresponds to a single experimental session.
- For each session, there might be multiple file formats, data modalities and recording systems. You should map them and choose the correct Neuroconv DataInterface for each data type.
- You should also check the metadata of the data files to understand the experimental protocols and conditions.

Task 2: creating a project
- You will be using the Neuroconv framework to convert the provided dataset into the NWB format.
- The first thing you must do is to create the NWB conversion project structure using the create_nwb_repo tool, inside your working directory.
- Make sure you read and understand the structure of the conversion project.
- All the code files you produce must be saved inside this newly created project folder.

Task 3: writing the data conversion code
- You should edit the files within the project folder to correctly convert the input data into the NWB format.
- The conversion should be done using Neuroconv. Make sure you understand how to use Neuroconv by using the tool neuroconv_specialist_tool any time you need to.
- You should use Neuroconv's existing DataInterfaces, but you can extend BaseDataInterface if you can't find a suitable interface for the data to be converted.
- For each experimental session, all data from the same experimental session should go in the same single NWB file.
- Ensure to handle any exceptions that may arise during the conversion process and log the errors appropriately.
- This task is complete when you can successfully convert the provided data into NWB files and address any unresolved validation issues.

Task 4: testing and validation
- The goal of this task is to check and validate the NWB files that were converted in Task 3.
- Use the "inspect_nwb_files" tool to validate the NWB files. If this tool responds with any errors or violations, you should go back to Task 3 and fix the issues.
- Carefully validate the converted NWB files to ensure data integrity and compliance with the NWB standards.
- Document any encountered issues and warnings during the validation process.
- Finish the task when all NWB files were tested.

Tasks 3 and 4 should happen iteratively until the NWB files are correctly formatted and passing all inspection tests.
