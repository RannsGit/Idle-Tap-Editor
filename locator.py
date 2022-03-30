import os
import sys
import subprocess

PARSED_FILENAME = "parsed.list"
WINDOWS = True if sys.platform == "win32" else False

#Import api if windows
if WINDOWS:
        import win32api, win32con

def main():

    #Find files
    files = getListOfFiles(getSpecifiedDirectory())

    #Get list of already computed files
    parsed = getParsedFiles()

    #Parse through files
    for file in files:
        #Skip if already evaluated
        if file in parsed: continue 

        #Reject if not .tap
        if file.split('.')[-1] != 'tap': continue

        #Parse & Document
        parse(file)
        addFileToParsed(file)
        
def parse(file):
    '''Calls header_mod.py with file as argument'''
    print(f"Parsed {file}")
    cmd = [sys.executable, "header_mod.py",r'"{}"'.format(file)]
    subprocess.call(cmd, shell=True)

def getSpecifiedDirectory():
    '''Reads the directory from the command line argumens.'''
    arg_error_msg = lambda x='': print(f"Error: {x}\nExpected: locator.py [directory]")
    sysArgs = sys.argv
    if len(sysArgs) < 2:
        arg_error_msg("No directory given")
    elif len(sysArgs) > 2:
        arg_error_msg("Too many arguments given")
    else:
        return sysArgs[1]
    exit()

def getParsedFiles():
    '''Get list of filenames that have already been parsed'''
    with open(PARSED_FILENAME, 'r') as parsedFiles:
        return parsedFiles.read().strip().split('\n')

def addFileToParsed(filename):
    '''Add filename to list of filenames that have been parsed'''
    os.system(f"echo {filename} >> parsed.list")

def dirHidden(p):
    '''Returns boolean indicating status of directory; hidden or not'''
    if WINDOWS:
        attribute = win32api.GetFileAttributes(p)
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    else:
        return p.startswith('.')

def getListOfFiles(dirName):
    '''For the given path, get the List of all files in the directory tree.'''
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    #print(f"listOfFile: {listOfFile}")

    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        if dirHidden(fullPath):
            continue
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

if __name__ == "__main__":
    main()