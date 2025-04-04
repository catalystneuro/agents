Your goal is to successfully convert a provided neurophysiology dataset (a.k.a. source data) into the NWB format. The process is divided into four main tasks:

1. investigate the source data and understand its types and recording systems.
2. create a conversion project for converting source data into the NWB format.
3. write the data conversion code and run the conversion process.
4. test and validate the converted NWB files.

General instructions:
- You should only create files inside the "/home/agent_workspace" directory.
- The source data is located in the "/home/data" directory.
- The output nwb files must be saved in the "/home/agent_workspace/converted_results" directory.

Task 1: investigate the source data
- You should explore the source data to understand its format and structure.
- Each folder inside "/home/data" corresponds to a single experimental protocol.
- Each protocol folder contains multiple session folders, and each session folder contains the data files.
- Each session might contain multiple file formats, data modalities, and recording systems. You should identify them all and choose the correct Neuroconv DataInterface for each data type.
- Make sure you diligently map all the experimental data types.
- You should also check the metadata.yaml of the sessions to understand the experimental protocols and conditions.

Task 2: creating a conversion project
- You will be using the Neuroconv framework to convert the provided dataset into the NWB format.
- The first thing you must do is to create the NWB conversion project structure using the `create_nwb_repo` tool, inside your working directory.
- Make sure you read the created files and understand the overall structure of the conversion project.
- All the code files, the ones you create and the ones you modify, must be kept inside this project folder.

Task 3: writing the data conversion code
- You should edit the files within the project folder to successfully convert the source data into the NWB format.
- The conversion should be done using Neuroconv. Make sure you understand how to use Neuroconv by using the tool `neuroconv_specialist_tool` any time you need to.
- You should use Neuroconv's existing DataInterfaces, but you can extend BaseDataInterface if you can't find a suitable interface for the data to be converted.
- For each experimental session, all data from the same experimental session should go in the same single NWB file.
- Ensure to handle any exceptions that may arise during the conversion process and log the errors appropriately.
- The output nwb files must be saved in the "/home/agent_workspace/converted_results" directory.
- This task is complete when you can successfully convert the provided data into NWB files and address any unresolved validation issues.

Task 4: testing and validation
- The goal of this task is to check and validate the NWB files that were converted in Task 3.
- Use the `inspect_nwb_files` tool to validate the NWB files. If this tool responds with any errors, violations or suggestions, you should go back to Task 3 and fix the issues.
- Carefully validate the converted NWB files to ensure data integrity and compliance with the NWB standards.
- Check if the organization of the "/home/agent_workspace/converted_results" directory is correct and matches the expected structure of one nwb file per protocol/session.
- Document any encountered issues and warnings during the validation process.
- Finish the task when all NWB files were tested.

Tasks 3 and 4 should happen iteratively until all the NWB files are correctly formatted and passing all inspection tests.

Example of the source data structure:
```
/home/data
├── protocol_1
│   ├── session_1
│   │   ├── data_file_1
│   │   ├── data_file_2
│   │   └── metadata.yaml
│   ├── session_2
│   │   ├── data_file_3
│   │   ├── data_file_4
│   │   └── metadata.yaml
└── protocol_2
    ├── session_3
    │   ├── data_file_5
    │   ├── data_file_6
    │   └── metadata.yaml
    ├── session_4
        ├── data_file_7
        ├── data_file_8
        └── metadata.yaml
```

Example of converted_results structure:
```
/home/agent_workspace/converted_results
├── protocol_1
│   ├── session_1.nwb
│   ├── session_2.nwb
└── protocol_2
    ├── session_3.nwb
    └── session_4.nwb
```

Your goal will only be considered successful when:
- the converted_results directory is organized correctly, with one directory per protocol and one nwb file per session.
- all the NWB files are correctly formatted and pass all inspection tests.

Do not give up until you have successfully completed the goal!