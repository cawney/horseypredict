import os
import PyPDF2
import re

# Directory path
directory = "cards"
report = 'report.txt'

# Get list of files in the directory
files = os.listdir(directory)




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
# re_date = re.compile(r'[\w]+? \d{1,2}, \d{4} -')
re_date = re.compile(r'- (?P<date>[A-Za-z].+?\d{1,2}, \d{4}) -')
re_distance = re.compile(r'Distance: (?P<distance>.)+?On The')
re_race_purse = re.compile(r'Purse:\$(?P<money>[\d,]+?)(\s|\n)')
re_last_raced = re.compile(r'^Last Raced')
re_fractional_times = re.compile(r'^Fractional Times')
re_horse_name = re.compile(r'\s\b[A-Z ]+ ([A-Z]{2,3})?')
re_jockey = re.compile(r'\([A-Za-z]+, [A-Za-z]+\)')
re_last_raced_horse = re.compile(r'^([\w\d]|-{3})+? ')
re_trainers = re.compile(r'Trainers: ')
re_trainer = re.compile(r"\d+ - ([^;]+)")
re_owners = re.compile(r'Owners: ')


#################################################
# Functions
#################################################


# Extract data from txt files
def group_by_race(file):
    '''
    Extract data from dictionary and output it to a text file
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



def extract_data(dict):
    '''
    Extract data from a list and return a dictionary
    Put all the details inside race_dict, and nest it inside
    '''
    all_races = [] # A dictionary that holds the race dictionaries
    race_dict = {} # A dictionary that has all the race information in it
    with open(report, "w") as txt_file:
        race_dict = {}
        for key, value in dict.items():
            # race_dict['file'] = key
            txt_file.write("File: " + key + '\n\n')
            for key, value in value.items():
                race_dict = {}
                # print('key: ', key)
                # print(value) # This is the list of lines for the race
                extract_line_data(value, race_dict)
                # print(race_dict)
            # print(race_dict)
                all_races.append(race_dict)
        # print(all_races) # This is the list of dictionaries
        # print(len(all_races))
    return all_races
        

def extract_line_data(lines, dictionary):
    '''
    Extract the data from the lines that is important
    '''
    # print("Extracting line data")

    for i, line in enumerate(lines):
        # dictionary = {}
        if re_date.search(line):
            dictionary['date'] = re_date.search(line).group('date')
            dictionary['race number'] = re_race_number.search(line).group(1)
        if match := re_distance.search(line):
            distance = match.group().split(': ')[1].split(' On The')[0]
            dictionary['distance'] = distance
        if re_race_purse.search(line):
            purse = re_race_purse.search(line).group('money')
            dictionary['purse'] = purse
        if re_last_raced.search(line):
            start = i
            extract_race_data(lines, start, dictionary)
        if re_trainers.search(line):
            start = i
            extract_trainers(lines, start, dictionary)


def extract_race_data(lines, start, dictionary):
    '''
    Extract the race data from the lines, purpose is to get
    the horse name and the jockey and weight
    '''
    for i, line in enumerate(lines[start:], 0):
        # print(line)
        if re_jockey.search(line):

            jockey_place = str(i) + 'jockey'
            horse_place = str(i) + 'horse'
            weight_place = str(i) + 'weight'
            dictionary[jockey_place] = re_jockey.search(line).group()[1:-1]
            # Get location of jockey in string
            jockey_location = line.find(re_jockey.search(line).group())
            end_jockey = re_jockey.search(line).end()

            # Get the end of the last_race_horse
            last_raced_end = re_last_raced_horse.search(line[:jockey_location]).end()
            horse_name = line[last_raced_end:jockey_location].strip()
            dictionary[horse_place] = horse_name
            dictionary[weight_place] = line[end_jockey + 1:end_jockey + 4].strip()
        if re_fractional_times.search(line):
            break

def extract_trainers(lines, start, dictionary):
    """
    1. Get the lines that have trainer information
    2. Put those lines in a long string
    3. Isolate the trainer information (between '-' and ';')
    4. Add them to the dictionary in the order they appeared.
    """
    # print("starting trainer extraction")
    lines_for_trainers = ''
    for i, line in enumerate(lines[start:], 0):
        if re_owners.search(line):
            end = i
            print('found owners')
            break
        lines_for_trainers += line
    lines_for_trainers = lines_for_trainers.replace('\n', ' ')
    trainers = re.findall(re_trainer, lines_for_trainers)
    # Add the trainers to the dictionary
    for i, trainer in enumerate(trainers, 1):
        dictionary[str(i) + 'trainer'] = trainer


def write_report(dictionary, file):
    '''
    Write out the dictionaries to a text file
    '''
    #dictionary is the dictionary of dictionaries
    # value[i] is thelist
    with open(file, "w") as txt_file:
        for key, value in dictionary.items():
            txt_file.write("File: " + key + '\n\n')
            for i in value:
                txt_file.write("Race number: " + i + '\n')
                for n in value[i]:
                    txt_file.write(n)
            txt_file.write('\n\n')


#################################################
# Main
#################################################


# Convert the pdf files to text files
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


# Iterate over the files
for file in os.listdir(directory):
    if file.endswith(".txt"):
        race_dict = {}
        group_by_race(os.path.join(directory, file))
        file_race_dict[file] = race_dict


print(len(file_race_dict))
list_of_races = extract_data(file_race_dict)
for i in list_of_races:
    print(i)
    print('\n')

print("Done")