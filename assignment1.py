
"""
Created on Wed Jan 31 10:07:25 2024
Agenda: Automate the summary of the panel taste results
author: user

"""
import re
import os
import pandas as pd
from datetime import datetime, date

os.chdir('C:/Users/Med-Food-Lab/MFL/Med-Food-Lab - Documents/MFL - DRIVE/R&D/experiments')
# Call to the experiments meta file
experiments = pd.read_excel('Experiment Meta File.xlsx', sheet_name='DSP')

# Choodse directory
os.chdir('C:/Users/Med-Food-Lab/MFL/Med-Food-Lab - Documents/MFL - DRIVE/R&D/Tasting Panel')

# Import the Duo Trio Form 
results = pd.read_excel('duotrio_sd.xlsx', sheet_name='Form1')
results.columns
results = results.drop(columns=['Test 1 - Notes','Test 2 - Notes','Test 3 - Notes',
                                'Test 4 - Notes','Test 5 - Notes','Test 6 - Notes',
                                'Test 7 - Notes','Test 8 - Notes','Test 9 - Notes',
                                'Test 10 - Notes','Test 11 - Notes','Test 12 - Notes',
                                'Test 13 - Notes','Test 14 - Notes','Test 15 - Notes',
                                'Test 16 - Notes','Test 17 - Notes','Test 18 - Notes',
                                'Test 19 - Notes','Test 20 - Notes'])

#Import the Trinalge key sheet
rows_to_skip = list(range(2, 1600)) 

key = pd.read_excel('Duotrio_sd_Key.xlsx', skiprows=rows_to_skip)

#convert the date time format for an Israeli format
key['Date'] = key['Date'].dt.date
results['Tasting Number'] = results['Tasting Number'].dt.date
# The tasting results take the key df, the results df and a date in a format of yyyy-m-dd

test_date = date(2024, 7, 9)
tasting_number = test_date


key = key[(key['Date'] == test_date)]

key = key[['Test','Sample id','Type']]

def find_odd_rows(df, test_column, sample_column):
    odd_tests = []
    odd_sample_id = []
    reference = []
    # Iterate through the DataFrame in steps of 3 rows
    for start in range(0, len(df), 3):
        # Create a small DataFrame with 3 rows
        batch_df = df.iloc[start:start + 3]

        # Check if batch_df has at least one row
       
        if not batch_df.empty:
            # Find the unique or odd string in the second column
            odd_row = batch_df[batch_df[sample_column] != batch_df[sample_column].mode()[0]]
            reference_row = batch_df[batch_df[sample_column] == batch_df[sample_column].mode()[0]]
            # Extract the value from the "test" column
            if not odd_row.empty:
                #Append the odd test to a list
                odd_value = odd_row[test_column].values[0]
                odd_tests.append(odd_value)
                # Append the sample id to a list
                odd_sample = odd_row[sample_column].values[0]
                odd_sample_id.append(odd_sample)
                # Append the reference to a list
                r_value = reference_row[sample_column].values[0]
                reference.append(r_value)
    return odd_tests, odd_sample_id , reference

odd_tests_list, odd_sample_id, reference = find_odd_rows(key, 'Test', 'Sample id')

####### Key results are arranged ######
############# Stage 2 analyse the tasting results #############################

def change_value(val):
    return 1 if val in odd_tests_list else 0


# Filter results by date
results = results[(results['Tasting Number']==tasting_number)]
results = results.drop(columns=['Tasting Number'])
results.columns = results.columns.str.strip()

''' 
There is two options for the comment part. With and without.
With will be the first comment and without will be the second one:
'''

''' WITH'''
#Change the COMMENT columns name and connect between the comments of the tasters

# def concatenate_notes(row, odd_column_name, notes_column_name):
#     # Ensure the notes column value is treated as a string
#     note = str(row[notes_column_name])
#     # Check if the value in the specified odd column is 1
#     if row[odd_column_name] == 1:
#         # Return the note in lowercase
#         return note.lower()
#     else:
#         # Otherwise, return an empty string
#         return ''

# notes_column_names = [f'Test {j} - Notes' for j in range(1, len(results.columns)//3 + 1)]

# # Rename columns to align with the generated notes column names
# for i in range(4, len(results.columns), 3):
#     if i <= len(results.columns) - 1:
#         results.rename(columns={results.columns[i]: notes_column_names[(i-4)//3]}, inplace=True)
        
# # Filter the DataFrame based on a condition 
# filtered_results = results

# # Apply the concatenate_notes function for each pair of odd and notes columns and concatenate the results
# comments_per_test = ['| '.join(filtered_results.apply(concatenate_notes, axis=1,
#                                                       args=(odd_column_name, notes_column_name)).dropna())
#                       for odd_column_name, notes_column_name in zip(odd_column_names, notes_column_names)]

'''WITHOUT'''

# # Insert empty values for the comments columns
# # Generate notes column names based on every third column, starting from the first group of three
# notes_column_names = [f'Test {j} - Notes' for j in range(1, len(results.columns)//3 + 1)]

# # Rename columns and clear any existing comments in these columns
# for i in range(4, len(results.columns), 3):
#     if i <= len(results.columns) - 1:
#         new_column_name = notes_column_names[(i-4)//3]
#         results.rename(columns={results.columns[i]: new_column_name}, inplace=True)
#         # Set all entries in this column to an empty string, clearing previous comments
#         results[new_column_name] = ''


# Drop unnecessary columns
results = results.dropna(axis=1)

# Count the number of tasters
n_tasters = len(results['Name'])

#Change the ODD columns name
p_odd_identification = []
odd_column_names = []

j = 1
for i in range(2, len(results.columns), 2):
    if i < len(results.columns):
        new_name = f"odd {j}"
        results.rename(columns={results.columns[i]: new_name}, inplace=True)
        results[new_name] = results[new_name].apply(change_value)

        odd_column_names.append(new_name)

        # Calculate the sum of '1's in the 'odd j' column
        sum_of_ones = results[new_name].sum()

        # Calculate the percentage
        percentage_of_odd = sum_of_ones / n_tasters
        p_odd_identification.append(percentage_of_odd)
        j += 1

#Change the COMPARED TO THE R columns name
j=1
for i in range(3, len(results.columns), 2):

    if i < len(results.columns):
        # Rename the column
        new_name = f"Score {j}"
        results.rename(columns={results.columns[i]: new_name}, inplace=True)
        j += 1


# Calculate the score of the each test
score_list = []
same_to_r = []
count_same = []
count_different = []
j = 1
for test in range(3, len(results.columns), 2):
    temp_score = []  
    temp_same_to_r = []
    temp_count_same = []
    temp_count_different = []
    temp_df = results[[f'odd {j}', f'Score {j}','Name']]
    temp_df.reset_index(drop=True, inplace=True) 
    for i, row in temp_df.iterrows():
        odd_value = row[f'odd {j}']
        compared_r_value = row[f'Score {j}']

        if odd_value == 1:
            if compared_r_value == 'Different':
                temp_score.append(-1)
                temp_count_different.append(1)
            elif compared_r_value == 'Same':
                temp_score.append(1)
                temp_count_same.append(1)
                temp_same_to_r.append(1)
        else:
            temp_score.append(1)
            temp_same_to_r.append(1)

    sum_test = sum(temp_score)
    score_list.append(sum_test/n_tasters)
    
    sum_same = sum(temp_same_to_r)
    same_to_r.append(sum_same/n_tasters)
    
    count_same.append(sum(temp_count_same))
    count_different.append(sum(temp_count_different))

    j += 1

score_list = [round(num, 1) for num in score_list]

######## Stage 3 insert the results to the summarize tasting results ##########

samples_followup = pd.read_excel('Trio_Followup.xlsx', sheet_name='Trio')


df = pd.DataFrame(columns=samples_followup.columns)
# insert the results of the tasting test into a new df. 
df['Sample id'] = odd_sample_id
df['Reference'] = reference
df['Date'] = df['Date'].fillna(test_date)

df['Notes'] = ["" for i in range(len(odd_sample_id))]

df['Go to QDA?'] = ["" for i in range(len(odd_sample_id))]
df['Odd Identification [%]'] = p_odd_identification
df['Difference standardize score'] = score_list
df['Same to the R [%]'] = same_to_r
df['Count Different (only Odd=1)'] = count_different
df['Count Better (only Odd=1)'] = ["" for i in range(len(odd_sample_id))]
df['Count Worse (only Odd=1)'] = ["" for i in range(len(odd_sample_id))]
df['Count Same (only Odd=1)'] = count_same
df['n tasters'] = df['n tasters'].fillna(n_tasters)
df['Type'] =  key.iloc[::3, 2].tolist()
# df['Go to QDA?'] = df['Go to QDA?'].apply(lambda x: f"{x * 100:.0f}%")
df['Same to the R [%]'] = df['Same to the R [%]'].apply(lambda x: f"{x * 100:.0f}%")
df['Odd Identification [%]'] = df['Odd Identification [%]'].apply(lambda x: f"{x * 100:.0f}%")
# Choose only the needed columns
df = df[['Date', 'Test Number', 'Sample id', 'Reference','Type','n tasters',
        'Odd Identification [%]', 'Count Different (only Odd=1)',
        'Count Better (only Odd=1)', 'Count Worse (only Odd=1)','GC Tested',
        'Count Same (only Odd=1)', 'Same to the R [%]', 'Go to QDA?','SUB+STR',
        'SUM Difference score', 'Difference standardize score', 'Notes','LC tested']]

############# Stage 4 - Merge tables and insert samples inputs ################

experiments = experiments[['Sample id', 'description', 'BC_substrate',
                            'strain','product_pH','product_Brix','Setting ']]

experiments = experiments.rename(columns={ 'BC_substrate':'Substrate',
                                          'description':'Description','strain':'Strain'})


##########################################################

# Standardize 'Sample id' to strings in both dfs to ensure consistency
experiments['Sample id'] = experiments['Sample id'].apply(lambda x: f"{int(x):d}" if pd.notnull(x) else x)
df['Sample id'] = df['Sample id'].astype(str)

# Prepare a new dataframe for merging by selecting 'Sample id' from 'df'
experiments_to_merge = pd.DataFrame()
experiments_to_merge['Sample id'] = df['Sample id']

# Merge 'experiments_to_merge' with 'experiments' on 'Sample id'
experiments_merged = experiments_to_merge.merge(experiments, how='left', on='Sample id')

# Merge the modified 'experiments' data into 'df'
df = df.merge(experiments_merged, how='left', on='Sample id')


##########################################################

df = df.drop_duplicates()
# Arranges all the columns in the order of original order
df = df[['Date', 'Test Number', 'Sample id', 'Reference', 'Type', 'product_Brix',
       'Description', 'Substrate', 'Strain', 'n tasters',
       'Odd Identification [%]', 'Count Different (only Odd=1)',
       'Count Better (only Odd=1)', 'Count Worse (only Odd=1)',
       'Count Same (only Odd=1)', 'Same to the R [%]', 'Go to QDA?',
       'SUM Difference score', 'Difference standardize score', 'Notes',
       'product_pH', 'LC tested', 'GC Tested', 'SUB+STR', 'Setting ']]


sub_str = df['Substrate'].str.cat(df['Strain'].astype(str), sep= " ")
df['SUB+STR'] = sub_str
##########################################################
#function to find sample number in blends
def find_sample_id(line):
    pattern = r'\b\d+\b'  # Matches sequences of digits (\d+)
    matches = re.findall(pattern, line)
    
    sample_num = []
    for match in matches:
        if match.isdigit():
            sample_num.append(match)
    
    if len(sample_num) == 1:
        return sample_num[0]
    else:
        return None


def update_curr_val_by_reference(line):
    ref = line[-1]
    strain = None
    if ref == 'A':
        ref = 'CP'
        strain = '1001'
    if ref == 'B':
        ref = 'CP'
        strain = '1003'
    if ref == 'C':
        ref = 'SFS'
        strain = '1001'
    if ref == 'D':
        ref = 'SFF'
        strain = '1001'
    if ref == 'E':
        ref = 'CPC'
        strain = '1001'
    if ref == 'F':
        ref = 'BW'
        strain = '1001'
    if ref == 'Y':
        ref = 'Yeast'
        strain = '1001'
    if ref == 'P':
        ref = 'Potato'
        strain = '1001'
    return ref, strain


#go over core-blend samples rows and update the important columns

for index, row in df.iterrows():
    #if core blend- find sample id
    if row['Type'] == 'Core blend':
        curr_sample = find_sample_id(row['Sample id'])
        if curr_sample is None:
            continue 
       #update the columns for the sample
        df.loc[index,'Description'] = experiments.loc[curr_sample,'description']
        df.loc[index,'Substrate'] = experiments.loc[curr_sample,'BC_substrate']
        df.loc[index,'Strain'] = experiments.loc[curr_sample, 'strain']
        df.loc[index,'setting'] = experiments.loc[curr_sample , 'setting']
       
    if pd.isnull(df.loc[index, 'Substrate']):
        df.loc[index, 'Substrate'] , df.loc[index, 'Strain'] = update_curr_val_by_reference(df.loc[index,'Reference']) 



##########################################################
# Adding empty columns after each "Score n" column.
unique_col_counter = 1
for col in results.columns:
    if col.startswith("Score"):
        col_index = results.columns.get_loc(col)
        results.insert(col_index + 1, f"Emptycol_{unique_col_counter}", "")
        unique_col_counter += 1



######### Stage 5 - Insert the tasting results to the final df ################
os.chdir('C:/Users/Med-Food-Lab/Desktop/rotem')
df.to_csv(f'final_results {test_date}.csv', index=False)
results.to_csv(f'duo_trio_results {test_date}.csv', index=False)



###################################################################



