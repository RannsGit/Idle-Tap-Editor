from datetime import datetime
import sys

#Lines in which to remove from the program
TARGET_LINES = [
    "M5",
    "G28 G91 Z0.",
]

class Gcode:
    def read(self):
        '''Returns text of self.filename'''
        return open(self.filename).read()
    def write(self, text):
        '''Takes text given as argument and writes to defined filename'''
        open(self.filename, 'w').write(text)
    def __init__(self, filename):
        self.filename = filename
        self.text = self.read()

def get_filename() -> str:
    '''Reads the filename from the command line argumens.'''
    arg_error_msg = lambda x='': print(f"Error: {x}\nExpected: header_mod.py [filename]")
    sysArgs = sys.argv
    if len(sysArgs) < 2:
        arg_error_msg("No filename given")
    elif len(sysArgs) > 2:
        arg_error_msg("Too many arguments given")
    elif not("tap" in sysArgs[1].split('.')[-1].lower()):
        arg_error_msg(f"Invalid filetype .{sysArgs[1].split('.')[-1]}")
    else:
        return (sysArgs[1]).strip('"')
    exit()

def get_blacklist():
    '''Get list of blacklisted lines'''

    blacklist = []

    with open("blacklist.txt", 'r') as bf:
        for line in bf.readlines():

            #Skip if empty line
            if line.strip() == '': continue
            
            blacklist.append(line.strip()) 
    return blacklist

def time_format(time):
    '''Reads the given time as a normal 12 Hour readout'''
    return time.strftime('%Y-%m-%d %I:%M %p')

def main():
    #Find filename & set gcode instance
    filename: str = get_filename()
    gcode = Gcode(filename)

    #Set header
    parsed = f"(Evaluated and edited at {time_format(datetime.now())})\n"

    #Print to console
    print(f"Parsed: {filename}")

    #Parse through lines to see if they contain the blacklisted lines
    for line in gcode.text.split('\n'):
        if line in TARGET_LINES:
            continue 
        if "Evaluated" in line:
            continue
        parsed += f"{line}\n"

    #Write results to file
    gcode.write(parsed)


if __name__ == "__main__":
    print(get_blacklist())

