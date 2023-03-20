import os
import subprocess
import argparse
from pathlib import Path
import shutil
import zipfile
import glob
import pandas as pd
from pydub import AudioSegment

# Define arguments for running the script (specify input and output directories)
# Input directory is where the zip files and results.csv file are located
# Output directory is where the participant directories with .wav files will be stored (we will create a new directory for each experiment, session, and/or condition within this directory)

script_dir = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Please enter the full path of the input directory.', required=True)
parser.add_argument('-o', '--output', help='Please enter the full path of the output directory.', required=True)

args = parser.parse_args()

input_dir = Path(args.input)
output_dir = Path(args.output)


if not input_dir.exists():
    print("The input directory doesn't exist")
    raise SystemExit(1)
    
if not output_dir.exists():
    print("The output directory doesn't exist")
    raise SystemExit(1)


# unzip files in input directory
my_dir = str(input_dir)

my_zip = glob.glob(os.path.join(my_dir + '/*.zip'))

for directory in my_zip:
  with zipfile.ZipFile(directory) as zip_file:
      for member in zip_file.namelist():
          filename = os.path.basename(member)
          # skip directories
          if not filename:
              continue
    
          # copy file (taken from zipfile's extract)
          source = zip_file.open(member)
          target = open(os.path.join(my_dir, filename), "wb")
          with source, target:
              shutil.copyfileobj(source, target)


# Move R script to input directory, run it, and move it back (this is the R script from PCIbex to get the results file in a more readable format). I also added to the script to write a tidy version of the participant information

shutil.move('tidy_pcibex.R', input_dir)
os.chdir(input_dir)

r_script = subprocess.run('Rscript tidy_pcibex.R', shell=True)
r_script


shutil.move('tidy_pcibex.R', script_dir)
os.chdir(script_dir)


# rename audio files and convert to .wav format

pd.options.mode.chained_assignment = None

# Open the csv file here you need to indicate the name of your csv file

name_csv_original = os.path.join(my_dir, 'my_results.csv')

file_csv_pd = pd.read_csv(name_csv_original)

# Create a column new_value_temporary where we will put the 0 indexed string (e.g undefined_session1_lista_naming -> undefined_session1_lista_naming-0)

file_csv_pd['new_value_temporary'] = ''



for ind in file_csv_pd.index:

    string_value = file_csv_pd['Value'][ind]

    if type(string_value) == str:

        if string_value.split('.')[-1] == 'webm':

            string_value_without_ext = string_value.split('.')[0]

            if string_value_without_ext != 'ac_recorder':

                if len(string_value_without_ext.split('-')) == 1:

                    file_csv_pd['new_value_temporary'][ind] = string_value_without_ext + '-0'

                else:

                    file_csv_pd['new_value_temporary'][ind] = string_value_without_ext

# Create a column new_value_one_indexed where we will change the 0 indexed values into 1 indexed values (start at 1 instead of 0 e.g. undefined_list1_block1-0 -> undefined_list1_block1-01)

file_csv_pd['new_value_one_indexed'] = ''



for ind in file_csv_pd.index:

    string_value = file_csv_pd['new_value_temporary'][ind]

    if string_value != '':

        value_string_without_trial = string_value.split('-')[0]

        index_0_value = int(string_value.split('-')[1])

        index_0_value +=1

        file_csv_pd['new_value_temporary'][ind] = value_string_without_trial + '_trial' + str(index_0_value).zfill(3)



# Create a column new_name_file with the new name of the file

file_csv_pd['new_name_file'] = ''


for ind in file_csv_pd.index:

    name_changed_webm = file_csv_pd['new_value_temporary'][ind]

    if name_changed_webm != '':

        name_target = file_csv_pd['Target'][ind]
        
        new_name = name_changed_webm + '_' + name_target
        new_name_list = new_name.split('_')
        new_name_list[0] = new_name_list[0][:5]
        new_name_string = '_'.join(new_name_list)

        file_csv_pd['new_name_file'][ind] =  new_name_string
        

# save the new csv with the last column with the new name

new_csv_name = name_csv_original.split('.')[0] + '_new_name_file_correspondance.csv'

file_csv_pd.to_csv(os.path.join(my_dir, new_csv_name))



# now we change the name of the webm files the old name are in the column 'Value', the new name in the column 'new_name_file'


for ind in file_csv_pd.index:
    try:
        string_value = file_csv_pd['Value'][ind]
        if type(string_value) == str:
            if string_value.split('.')[-1] == 'webm':
                string_value_without_ext = string_value.split('.')[0]
                if string_value_without_ext != 'ac_recorder':
                    old_name_webm = string_value
                    new_name_webm = file_csv_pd['new_name_file'][ind] + '.webm'
                    os.rename(os.path.join(my_dir, old_name_webm), os.path.join(my_dir, new_name_webm))
    except:
        print("Something went wrong!")


# now convert the webm files in the folder to wav files

# Get the list of all files
files_webm = glob.glob(os.path.join(my_dir + '/*.webm'))

# Convert from webm to wav

for f in files_webm:
    try:
        #print(f)
        wav_export_name = os.path.join(my_dir, f.split('.')[0] + '.wav')
        #print(wav_export_name)
        in_audio = AudioSegment.from_file(f,"webm")
        in_audio.export(wav_export_name, format="wav")
    except:
        print("Something went wrong!")


if not os.path.exists('webm_folder'):

    os.mkdir(os.path.join(my_dir, 'webm_folder'))


target_dir = os.path.join(my_dir, 'webm_folder')



for f in files_webm:

    shutil.move(os.path.join(my_dir, f), target_dir)



# create directory for each participant and move wav files there
tidy_path = os.path.join(input_dir, 'tidy.csv')
df = pd.read_csv(tidy_path)

for id in df["Prolific_ID_input"]:
    path = os.path.join(my_dir, id)
    os.mkdir(path)
    print("Directory '%s' created" %id)
    for file in os.listdir(my_dir):
        if file.startswith(id[:4]):
            file_path = os.path.join(my_dir, file)
            shutil.move(file_path, path)


# Create destination directory to move usable data to, and move it there

exp = input('Enter experiment number: ')
ses = input('Enter session number: ')
list = input('Enter list (A/B): ')
cond = input('Enter condition (NS/S): ')

folder_name = 'Exp' + exp + '_Session' + ses + '_List' + list + '_' + cond

destination_dir = Path(os.path.join(output_dir, folder_name))

if not os.path.isdir(destination_dir):
    os.makedirs(destination_dir)

for id in df['Prolific_ID_input']:
    path = os.path.join(my_dir, id)
    prompt = 'Can we use the data from participant ' + str(id) + '? (y/n) '
    data_qual = input(prompt)
    if data_qual == 'y':
        shutil.move(path, destination_dir)
    print('Done!')
