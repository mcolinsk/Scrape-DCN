#################
# handle files
# 
#################

# NOT USED
def filePicker(filetypes="*.csv *.xlsx",filetypes_desc="xlsx or csv files",include_all_files=True):
    #src: https://stackoverflow.com/questions/7994461/choosing-a-file-in-python3
    #src: https://stackoverflow.com/questions/3579568/choosing-a-file-in-python-with-simple-dialog
    #src: https://stackoverflow.com/questions/29174300/tkinter-window-not-closing-after-closed-file-dialog

    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter import filedialog
    import os
    homeFolder = os.path.expanduser('~')
    downloadsFolder = os.path.join(homeFolder, 'Downloads')

    root = Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    if(include_all_files):
        filepath =  filedialog.askopenfilename(initialdir = downloadsFolder,title = "Select file",filetypes = ((filetypes_desc,filetypes),("all files","*.*")))
    else:
        filepath =  filedialog.askopenfilename(initialdir = downloadsFolder,title = "Select file",filetypes = ((filetypes_desc,filetypes)))
    #filename = root.filename
    return filepath
    
def convert_json_to_csv(json_obj,filepath='',filename='data_file'):
    #src: https://www.geeksforgeeks.org/convert-json-to-csv-in-python/
    opssIndexObj = {
        "0":{
            "Type":"Prov",
            "No":"100",
            "Date":"Nov 2016"
        },
        "1":{
            "Type":"Prov",
            "No":"182",
            "Date":"Apr 2017"
        },
        "2":{
            "Type":"Prov",
            "No":"313",
            "Date":"Nov 2016"
        }
    }
    import csv
    from datetime import datetime
    import json

    # now we will open a file for writing 
    homeFolder = os.path.expanduser('~')
    downloadsFolder=""
    if len(filepath)>0:
        downloadsFolder=filepath
    else:
        downloadsFolder = os.path.join(os.path.expanduser('~'), 'Downloads')
        
    path = os.path.join(downloadsFolder, f'{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    data_file = open(path, 'w',newline='')
    
    # create the csv writer object 
    csv_writer = csv.writer(data_file) 

    # Counter variable used for writing  
    # headers to the CSV file 
    count = 0
    for row in json_obj: 
        if count == 0: 
    
            # Writing headers of CSV file 
            header = json_obj[row].keys() 
            csv_writer.writerow(header) 
            count += 1
    
        # Writing data of CSV file 
        csv_writer.writerow(json_obj[row].values()) 
    
    data_file.close() 
    
def check_jsonKeys(json_data,keys_array):
    # Check if keys exist in a json object
    # keys_array = ["No","Type","Date"]
    # json_data = {
    #         "Type":"Prov",
    #         "No":"100",
    #         "Date":"Nov 2016"
    #     }

    for key in keys_array:
        if not(key in json_data):
            print(f'Key: {key} is not in the obj')
            return False
    return True

# NOT USED
def get_file(filepath):
    if(not(filepath)):
        fileName = 'database.csv'
        homeFolder = os.path.expanduser('~')
        downloadsFolder = os.path.join(homeFolder, 'Downloads')
        pathToFile = os.path.join(downloadsFolder, fileName)
        

import os