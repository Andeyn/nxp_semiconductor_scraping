########### IMPORTING LIBRARIES ###########
from copy import deepcopy
from nis import cat
from posixpath import pardir
from itertools import count, islice
import time
import os
import csv
from bleach import clean
import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import re

########### REMOVES RENDUNDANT DATA ###########
# returns array of all scraped csv paths 
def grab_all_paths(directory):
    all_csv_paths = []
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    # loop over the list of csv files
    for f in csv_files:
        df = pd.read_csv(f)	
        filename = f.split("\\")[-1]
        all_csv_paths.append(filename)
    return all_csv_paths

# removes all duplicates in a single csv
def remove_dups(path):
    df  = pd.read_csv(path)

    seen = set()
    for index, row in df.iterrows():
        link = df.loc[index, 'links']
        seen.add(link)
    
    cleaned_df = pd.DataFrame(seen, columns=['links'])
    cleaned_df.to_csv(path, index=True)
    return None

# removes all duplicates in all csv's 
# (ONLY CALL ONCE TO CLEAN DATA INITIALLY)
def clean_all_csv():
    directory = '/Users/andeyng/Desktop/semiconductors/nxp'
    all_csv_paths = grab_all_paths(directory)
    for i in all_csv_paths:
        print(f'Cleaning: {i}')
        remove_dups(i)
    return None

########### PARSING DATA ###########
# grabs name of csv's by calling grab_all_paths
def grab_all_names(directory):
    all_csv_paths = grab_all_paths(directory)
    all_names = []
    for path in all_csv_paths:
        name = path[46:-4]
        all_names.append(name)
    all_names.sort()
    return all_names

# takes in dictionary
# returns dict with: {link: [category1, category2, etc.]}
def map_urls(directory):
    all_csv_paths = grab_all_paths(directory)
    d = {}
    for path in all_csv_paths: #reads each csv
        df  = pd.read_csv(path) 
        path_name = path[46:-4]
        for index, row in df.iterrows():
            link = df.loc[index, 'links']
            if link not in d:
                d[link] = [path_name]
            else:
                d[link].append(path_name)    
    return d

# initiates empty matrix of 0's
# returns dict of names and indices
def make_matrix_and_map(cat_names, size):
    name_map = {}
    matrix = [[0]*size for i in range(size)]
    for i in range(size):
        name = cat_names[i]
        name_map[name] = i
    return matrix, name_map

# indexes into matrix for each pair
# returns matrix of frequency count, and dictionary {pair: count}
def grab_and_place_pairs(d, matrix, names, name_map, matrix_path):
    pair_dict = {}
    for link in d:
        lst = d[link]
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                pair = [lst[i], lst[j]]
                pair.sort()
                tup_pair = tuple(pair)
                if tup_pair not in pair_dict:
                    pair_dict[tup_pair] = 1
                else:
                    pair_dict[tup_pair] += 1
                row, col = name_map[pair[0]], name_map[pair[1]]
                matrix[row][col] += 1
    pair_dict = dict(sorted(pair_dict.items(), key=lambda item: -item[1]))

    # matrix to df to csv
    matrix_df = pd.DataFrame(matrix, columns=names, index=names)
    matrix_df.to_csv(matrix_path)

    return matrix_df, pair_dict

# takes in dictionary of pair {pair_name: count}, and bucketsize range
# returns (list of dictionary, 2D lists) of {range: pair1&pair2}
def bucketing_pairs(pair_dict, bucketsize):
    dict_lst = []
    lst_total = []
    for lb in range(0,len(pair_dict), bucketsize):
        # dict_lst: appending [{(pair1, pair2): count}]
        hb = lb + bucketsize
        d = {k:v for k,v in pair_dict.items() if v > lb and v <= hb}
        if d != {}:
            dict_lst.append(d)

        # lst_total: appending [[count_range], [pairs]]
        col1 = [f'{lb}-{hb}']*len(d) 
        col2 = [k for k,v in pair_dict.items() if v > lb and v <= hb]
        col2_cleaned = []
        for i in col2:
            concat_pair_str = [f'{i[0]}&{i[1]}'] 
            col2_cleaned.append(concat_pair_str)
        range_and_pairs = [col1, col2_cleaned]
        if range_and_pairs[0] != []:
            lst_total.append(range_and_pairs)
    return dict_lst, lst_total

# takes list of ([[[ranges],[pair names]]], path)
# writing all the pairs into bucketed columns of a category [0-10: Auto&Industry]
def lst_pairs_csv(lst_total, path):
    cumulated_df = pd.DataFrame()
    for i in range(len(lst_total)-1, -1, -1): 
        pair = lst_total[i]
        if pair[0] != []: # catches empty lists
            col_name = [pair[0][0]]
            single_df = pd.DataFrame(pair[1], columns=col_name)
            cumulated_df = pd.concat([cumulated_df,single_df], ignore_index=False, axis=1)
        else:
            continue
    cumulated_df.to_csv(path)
    return None

# takes list of dictionary [{(pair1, pair2):count}], concatenates pair1&pair2 names
# returns horizontal bar charts of range of bucketsize
def visualizations(dict_lst, bucketsize):
    for i in range(len(dict_lst)):
        if i != {}:
            d = dict_lst[i]
            keys = [str(pair) for pair in d.keys()]
            values = list(d.values())
            fig = plt.figure(figsize = (10, 5))
            plt.barh(keys, values, color ='maroon')
            plt.xlabel("Category Pairs")
            plt.ylabel("Frequency")
            plt.title(f"Category Pair Frequency from {i*bucketsize} to {(i+1)*bucketsize}")
            plt.show()
    return None

############### FIGURES ###############
'''
Figure 1: (largest graph and title)  
- Cross-Sector of Sharing Semiconductor Chips (Datasheets and Datasheet Families)
    - Example - NXP Microprocessors and Microcontrol Units
- Bubble Graph 

Figure 2: (same axis)
- Largest Sharing of Semiconductor Chips Across Sector Subcategories: Example - NXP Microprocessors and MCUs
- Bar chart

Figure 3: (same axis)
- Shared Semiconductor Chips (Datasheets and Datasheet families) within Automotive Applications: Example - NXP Microprocessors and MCUs
- Bar chart

Figure 4: (same axis)
- Shared Semiconductor Chips (Datasheets and Datasheet families) within Industrial Applications: Example - NXP Microprocessors and MCUs
- Bar chart
'''

# FIGURE 1: major category matrix
# rename A1 cell to category_1 for data visualization in R 
def major_categories(matrix_df, names, path):
    for index, row in matrix_df.iterrows():
        if "_All" not in index:
            matrix_df.drop(index, inplace=True, axis=1)
    #dropping all rows if row name does not contain '_All'
    nameLst_without_alls = [name for name in names if '_All' not in name]
    df = matrix_df.drop(nameLst_without_alls)
    # df.to_csv(path)
    return df

# checks if pairs are in the same larger category
def is_same_category(pair1, pair2):
    pair1 = pair1.split("_")
    pair2 = pair2.split("_")
    return pair1[0] == pair2[0]

# checks if both pair1 and pair2 has the keyword 
def has_keyword(pair1, pair2, keyword):
    return (keyword in pair1) and (keyword in pair2)

# places space for 'Automotive_VehicleNetworking' to 'Vehicle Networking'
def format_keyword(word):
    words = word.split('_')
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]*', words[1])
    formatted_word = ' '.join(res_list)
    return formatted_word

# formats 'Industrial_FactoryAutomation' to 'Mobile: Wearables'
def format_semicolon(word):
    word = word.split('_')
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]*', word[1])
    word[1] = ' '.join(res_list)
    return f'{word[0]}: {word[1]}'

# FIGURE 2: largest subcategories with different group
def largest_subcategories_diff_group(pair_dict, top_shown, path):
    #create deepcopy to prevent aliasing in other functions
    pair_dict_copy = deepcopy(pair_dict) 
    # removes same category
    remove_pair_lst = []
    for pair in pair_dict_copy:
        if "_All" in pair[0] or "_All" in pair[1]:
            remove_pair_lst.append(pair)
        else:
            if is_same_category(pair[0], pair[1]):
                remove_pair_lst.append(pair)
    for pair in remove_pair_lst:
        pair_dict_copy.pop(pair)
    
    ###### CREATES CSV FOR TOP CATEGORIES ######
    df_lst, counter = [], 0
    for pair in pair_dict_copy:
        row = []
        if counter <= top_shown:
            row.append(f'{format_semicolon(pair[0])} & {format_semicolon(pair[1])}')
            count = pair_dict_copy[pair]
            row.append(count)
        else: 
            break
        df_lst.append(row)
        counter += 1
    df = pd.DataFrame(df_lst,columns=['Category_Pair_Name', 'Count'])
    df.to_csv(path)

    ######## CREATES MATPLOTLIB VISUAL #########
    # keys = [str(pair) for pair in pair_dict_copy.keys()]
    # keys = keys[:top_shown]
    # values = list(pair_dict_copy.values())
    # values = values[:top_shown]
    # fig = plt.figure(figsize = (10, 5))
    # plt.barh(keys, values, color ='maroon')
    # plt.xlabel("Frequency")
    # plt.ylabel("Subcategory Pairs")
    # plt.title(f"Top {top_shown} Overlap in Subcategory Pairs")
    # plt.show()  


# takes in d {(pair1, pair2): count,}, empty matrix, category names, name_map
# returns df of matrix of only this category
def keyword_commonality_matrix(d, matrix, cat_names, name_map, path):
    for i in d:
        pair = [i[0], i[1]]
        row, col = name_map[pair[0]], name_map[pair[1]]
        matrix[row][col] = d[i]
    formatted_cat_names = [format_keyword(name) for name in cat_names]
    keyword_matrix_df = pd.DataFrame(matrix, columns=formatted_cat_names, index=formatted_cat_names)
    keyword_matrix_df.to_csv(path)
    return keyword_matrix_df

# FIGURE 3 & 4: Commonality within Automotive Applications
def sector_commonality(pair_dict, keyword, path):
    #create deepcopy to prevent aliasing in other functions
    pair_dict_copy = deepcopy(pair_dict)
   
    # removes any categories containing 'All' and doesn't have keyword
    remove_pair_lst = []
    for pair in pair_dict_copy:
        if "_All" in pair[0] or "_All" in pair[1]:
            remove_pair_lst.append(pair)
        elif not has_keyword(pair[0], pair[1], keyword):
            remove_pair_lst.append(pair)
    for pair in remove_pair_lst:
        pair_dict_copy.pop(pair)

    # creating list of all categories
    cat_names = set()
    for pair in pair_dict_copy:
        cat_names.add(pair[0])
        cat_names.add(pair[1])
    cat_names = list(cat_names)
    matrix, name_map = make_matrix_and_map(cat_names, len(cat_names))
    keyword_commonality_matrix(pair_dict_copy, matrix, cat_names, name_map, path)



########### MAIN FUNCTION ###########
def main():
    directory = '/Users/andeyng/Desktop/semiconductors/nxp_pmc'
    cat_names = grab_all_names(directory)
    matrix, name_map = make_matrix_and_map(cat_names, len(cat_names))
    url_dict = map_urls(directory)

    # TO DO: change the path to respective local path
    matrix_path = '/Users/andeyng/Desktop/semiconductors/matrix_count.csv'
    matrix_df, pair_dict = grab_and_place_pairs(url_dict, matrix, cat_names, name_map, matrix_path) 

    # TO DO: change the path to desired bucketsize
    bucketsize = 10 
    dict_lst, lst_total = bucketing_pairs(pair_dict, bucketsize)
    # TO DO: change the path to respective local path
    pair_path = '/Users/andeyng/Desktop/semiconductors/pair_count.csv'
    lst_pairs_csv(lst_total, pair_path)
    
    ###### VISUALIZATION: BUCKETS OF RANGES ######
    # visualizations(dict_lst, bucketsize)

    # FIGURE 1 TO DO: change the path to respective local path
    major_categories_path = '/Users/andeyng/Desktop/semiconductors/major_categories.csv'
    major_categories(matrix_df, cat_names, major_categories_path)
    
    # FIGURE 2 TO DO: change the path to respective local path
    largest_subcategories_diff_group_path = '/Users/andeyng/Desktop/semiconductors/largest_subcategories_diff_group.csv'    
    largest_subcategories_diff_group(pair_dict, 10, largest_subcategories_diff_group_path)
    
    # FIGURE 3 TO DO: change the path to respective local path
    automotive_commonality_path = '/Users/andeyng/Desktop/semiconductors/automotive_commonality.csv'    
    sector_commonality(pair_dict, 'Automotive', automotive_commonality_path)

    # FIGURE 4 TO DO: change the path to respective local path
    industrial_commonality_path = '/Users/andeyng/Desktop/semiconductors/Industrial_commonality.csv'    
    sector_commonality(pair_dict, 'Industrial', industrial_commonality_path)
    return None

if __name__ == "__main__":
    main()