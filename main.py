import os
import PyPDF2
import re

# Directory path
directory = "cards"

# Get list of files in the directory
files = os.listdir(directory)

# Iterate over the files
for file in files:
    # Check if the file is a PDF file
    if file.endswith(".pdf"):
        # Open the PDF file
        with open(os.path.join(directory, file), "rb") as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract the text from each page
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        # Save the extracted text to a text file
        with open(os.path.join(directory, file.replace(".pdf", ".txt")), "w") as txt_file:
            txt_file.write(text)


#################################################
# Variables
#################################################

race_type = ''
race_number = ''
race_date = ''
distance = ''
race_dict = {}
file_race_dict = {}
day_list = []

########################
# Regex
########################

re_race_number = re.compile(r'- Race (\d+)')
re_date = re.compile(r'[\w]+? \d{1,2}, \d{4}')
re_distance = re.compile(r'Distance:(?P<distance>.)+?On the')



#################################################
# Functions
#################################################


# Extract data from txt files
def extract_data(file):
    '''
    Extract the data from the text file and put it in a dictionary so you can access it later
    '''
    with open(file, "r") as txt_file:
        lines = txt_file.readlines()
    
    race_lines = []
    for i, line in enumerate(lines):
        if re_race_number.search(line):
            if race_lines:
                race_dict[race_number] = race_lines
                race_lines = []
            race_number = re_race_number.search(line).group(1)
        
        race_lines.append(line)
    
    if race_lines:
        race_dict[race_number] = race_lines

# Iterate over the files
for file in os.listdir(directory):
    if file.endswith(".txt"):
        race_dict = {}
        extract_data(os.path.join(directory, file))
        file_race_dict[file] = race_dict

# Print the dictionary
for key, value in file_race_dict.items():
    print("Key: ", key)
    print("Value: ", value)
    print('\n')

# file_race_dict has a dictionary for each file
# race_dict is a dictionary of each day's races.

print("Done")