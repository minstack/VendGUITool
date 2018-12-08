import csv
from collections import defaultdict
import datetime as dt
from os.path import expanduser

def getColumn(csvFile, colName):
    """
        Processes the provided CSV and retrieves and returns the column values
        of the specified column name. Taken from stack overflow.
    """
    columns = defaultdict(list) # each value in each column is appended to a list

    with open(csvFile, newline='') as f:
        reader = csv.DictReader(f) # read rows into a dictionary format
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value
                columns[k].append(v) # append the value into the appropriate list
                                     # based on column name k
    return columns[colName]

def writeListToCSV(list, colHeader, title, prefix):
    """
        Exports the provided array into a column with the provided column header
        as a CSV file with specified title as suffix to filename.
        Filename format: [prefix][datetime][title].csv
    """
    if colHeader:
        list.insert(0, colHeader)

    filename = prefix + dt.datetime.now().strftime("%Y-%m-%dT%H:%M") + title + ".csv"

    #gui.setStatus("Writing {0}...".format(filename))

    desktop = expanduser("~") + '/' + 'Desktop/'

    with open(desktop + filename, "w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"',quoting=csv.QUOTE_ALL)
        for row in list:
            writer.writerow([row])

    #gui.setStatus("Write {0} completed...".format(filename))

    return filename
