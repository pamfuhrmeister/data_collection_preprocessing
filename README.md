# pcibex
Description:  
Python and R scripts to make pre-processing of speech production data collected with Prolific/PCIbex easier

Why:  
When collecting speech production data through Prolific/PCIbex, there are a lot of files that have to be moved various places, and doing this can be error prone. 
The goal of this pipeline is to reduce some of the manual labor involved to be more efficient and less error prone.


Help documentation:

usage: 
```
pcibex.py [-h] -i INPUT -o OUTPUT

optional arguments: 
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Please enter the full path of the input directory.
  -o OUTPUT, --output OUTPUT
                        Please enter the full path of the output directory.
```
                                              
What the pipeline does: 
1. Unzips all zip files in the directory (participant audio files are saved to the server in zip files)
2. Moves the R script to the input directory and calls it; this cleans up the results file (writes a new file called my_results.csv) and writes a csv file that is a tidy version of the information we ask participants to provide in a questionnaire (tidy.csv)
3. Renames audio files to include trial number and name of object and converts them to .wav format (they are originally in .webm format); writes a new file called my_results_new_name_file_correspondance.csv; creates a directory for the webm files and moves them all there
4. Creates a directory for each participant (one directory for each participant number in tidy.csv file) and moves the audio files that correspond to that participant there
5. Creates a destination directory to move usable data to (unless the directory already exists); prompts user for input for various attribues of the experiment to name this directory
    - For the current example, we used the experiment number, session number, list, and condition. This can be customized on lines 222-227 of pcibex.py
6. User checks data for each participant manually. Script prompts the user to say whether the data for each participant is usable
    - If so, it moves the participant directory with all the audio files to the destination directory that was just created
    - If not, the directory remains where it is


Instructions for using the pipeline:

Setup: 

Create a directory (anywhere on your computer) that includes the following: 
- Participant's audio files saved to server (zip files)
- Results file generated from PCIbex (can include more participants than you have audio files for); this needs to be named results.csv

Create a directory (anywhere on your computer) that includes the following files: 
- pcibex.py
- tidy_pcibex.R

To run the pipeline:  
- Open a terminal and navigate to the directory that includes the two files (on a mac this is cd path/to/directory)
- Type python pcibex.py -i path/to/input/directory -o path/to/output/directory
  + Input directory is where the zip files and results file are
  + Output directory is the root directory for where you want to create a new directory for each experiment/session/condition/etc. to move the audio files to
- Follow prompts
  
