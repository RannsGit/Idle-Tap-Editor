"""
Parse and remove all illegal gcode lines in all .tap files found in a drive.

Kyle Tennison
September 16, 2022
"""

import subprocess
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import stat
from typing import Callable

DEBUG = False

# Check if windows OS
IS_WINDOWS = False
if sys.platform == "win32":
        if DEBUG: print("importing windows packages")
        import win32api, win32con
        IS_WINDOWS = True


class Locator:

    PARSED_FILENAME = "parsed.list"

    def __init__(self, root: str):
        """Check for OS type and for specified root directory"""

        self.root = root

    @classmethod
    def getParsedFiles(cls) -> list:
        """Get a list of filenames that have already been parsed"""
        with open(cls.PARSED_FILENAME, "r") as parsedFiles:
            return [i.split(": ")[-1] for i in parsedFiles.read().strip().split("\n")]

    @classmethod
    def addFileToParsed(cls, filename: str) -> None:
        """Add filename to list of filenames that have been parsed"""
        with open(cls.PARSED_FILENAME, "a") as p:
            p.write(f"{datetime.now()}: {filename}\n")

    @staticmethod
    def isTap(filename: str) -> bool:
        """Checks if a filetype is tap"""
        return filename.split(".")[-1].lower() == "tap"

    @classmethod
    def isDuplicate(cls, filename: str) -> bool:
        """Checks if a file has already been parsed"""
        return filename in cls.getParsedFiles()

    @staticmethod
    def dirHidden(filepath: str) -> bool:
        """Returns boolean indicating visibility status of a directory; hidden=True"""

        if IS_WINDOWS:
            return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        else:
            return filepath.startswith(".")


    def listFiles(self, path:str =None, 
                  log: Callable[[str], any]=print) -> list:
        """For the given path, get the List of all files in the directory tree."""
        assert self.root != None, "root cannot be None type"
        
        # Default root path
        if path is None:
            path = self.root

        # Names in the given directory
        try: 
            listOfFile = os.listdir(path)
        except PermissionError:
            log(f"Insufficient permissions: {path}")
            listOfFile = []
            
            

        allFiles = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(path, entry)
            if self.dirHidden(fullPath):
                continue
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath) and fullPath != '':
                allFiles = allFiles + self.listFiles(fullPath, log=log) # recurse
            else:
                allFiles.append(fullPath)
                    
        return allFiles 
    
class Gcode:
    """Object representing gcode file."""

    def __init__(self, filename):
        self.filename = filename 

    def read(self) -> str:
        """Returns the full text of gcode file"""
        with open(self.filename, "r") as gcodeFile:
            return gcodeFile.read()
    
    def write(self, text: str) -> None:
        """Write to gcode file"""
        with open(self.filename, "w") as gcodeFile:
            gcodeFile.write(text)

    @property 
    def text(self) -> str:
        return self.read()

    @text.setter
    def text(self, text:str) -> None:
        self.write(text)

class Parser:
    """Tools to find and parse files."""

    BLACKLIST_FILENAME = "blacklist.txt"

    def __init__(self):
        
        self.blacklisted = self.getBlacklisted()
        self.header = \
            f"(Evaluated and edited at {self.timeFormat(datetime.now())})\n"
    
    @staticmethod
    def timeFormat(time: datetime) -> str:
        """Reads the given time as a normal 12 Hour readout"""
        return time.strftime("%Y-%m-%d %I:%M %p")

    @classmethod
    def getBlacklisted(cls) -> list:
        blacklist = []

        with open(cls.BLACKLIST_FILENAME, "r") as bf:

            for line in bf.readlines():

                # Only parse nonempty lines
                if line.strip():
                    blacklist.append(line.strip())
        
        return blacklist

    def parseFile(self, filename: str=None) -> None:
        """Parse and edit file for blacklisted text"""

        # Update file if give 
        if filename is not None:
            self.setFile(filename)
        
        fileContents = self.header

        for line in self.gcode.text.split("\n"):
            # Skip blacklisted lines
            if line in self.blacklisted:
                continue 

            # Skip previous header lines
            if self.header[:8] in line:
                continue

            # Add line to file contents
            fileContents += f"{line}\n"

        self.gcode.write(fileContents)  # Write results to file

    def setFile(self, filename: str) -> None:
        """Change or set the gcode file to a filename"""
        self.gcode = Gcode(filename=filename)
        self.filename = filename

class ParserApp:
    """Composite Parser and Composite class intended for higher level use."""

    LOGFILE = "log.txt"

    def __init__(self, root: str):

        # Move os to current dir
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.locator = Locator(root=root)
        self.parser = Parser()
        self._root = root
    
    def parseAll(self, log: Callable[[str], any]=print, 
                 altLog: Callable[[str], any]=lambda a: None) -> None:
        """Parse all files and sub-files in the current root directory"""
        # Get All Files
        rootfiles = self.locator.listFiles(log=altLog)

        # Scan through all files
        for file in rootfiles:
            altLog(file)

            # Pick out tap files
            if self.locator.isTap(file):

                if not self.locator.isDuplicate(file):
                    log(file)

                    # Parse file
                    self.parser.setFile(file)
                    self.parser.parseFile()

                    # Mark as parsed
                    self.locator.addFileToParsed(file)
    
    def clearLog(self) -> None:
        """Clear previously parsed filenames"""
        with open(self.locator.PARSED_FILENAME, "w") as pf:
            pf.write("") # Clears Log

    def changeRoot(self, newRoot: str) -> None:
        """Change root directory for searching"""
        del self.locator
        self.locator = Locator(root=newRoot)

    def fileLog(self, text: str) -> None:
        """Log console to file"""
        with open(self.LOGFILE, "a") as logfile:
            logfile.write(f"{datetime.now()}: {text}\n")

    def filelogbegin(self) -> None:
        """Add new header to logfile on each startup"""
        with open(self.LOGFILE, "a") as logfile:
            logfile.write(f"\n\t~~~~~  NEW LOGIN @ {datetime.now()} ~~~~~\n")

class ParserGui(tk.Tk):

    PFCONSOLE_MAX_LINES = 12
    SFCONSOLE_MAX_LINES = 15
    BUTTON_WIDTH = 40 if IS_WINDOWS else 13
    AUTOPARSE_DELAY = 30

    def __init__(self, *args, **kwargs):
        """Setup Parser Gui"""
        super().__init__(*args, **kwargs)

        self.parserApp = ParserApp(os.getcwd())
        self.parserApp.filelogbegin()  # begin log

        # Set icon
        self.iconbitmap("icon.ico")

        # Parsed Files Console Setup
        self.pfConsoleLines = [" " for i in range(self.PFCONSOLE_MAX_LINES + 1)]
        self.pfConsoleTextVar = tk.StringVar()
        self.pfConsoleTextVar.set("\n".join(self.pfConsoleLines))

        # Searched Files Console Setup
        self.sfConsoleLines = [" " for i in range(self.SFCONSOLE_MAX_LINES + 1)]
        self.sfConsoleTextVar = tk.StringVar()
        self.sfConsoleTextVar.set("\n".join(self.sfConsoleLines))
        self.sfConsoleRefreshCount = 0

        # Misc Setup
        self.currentRootTextVar = tk.StringVar(value="Current root: " + os.getcwd())

        # Countdown Timer Setup
        self.lastParse = datetime.now()
        self.autoParseLabelText = tk.StringVar()

        # Allow for parse block
        self.blockParse = False

        # Make and place widgets
        self.setup()

        # Add logout method
        self.protocol("WM_DELETE_WINDOW", lambda *args, **kwargs: exit())

        # Start background refresh
        self.backgroundRefresh()
        self.after(1000, self.backgroundRefresh)

    def setup(self) -> None:
        """Build and place tk objects on window"""

        # ----- Window Config -----

        self.title("G Code Parser")
        self.resizable(width=True, height=False)

        # ----- Widgets Build -----

        heading = ttk.Label(
            self,
            text = "Gcode Parser",
            font = (
                "Arial",
                24,
                "bold"
            ),
            padding=(10,10)
        )

        parseNowButton = ttk.Button(
            self,
            text = "Parse Now",
            command = self.parseNow,
            width=self.BUTTON_WIDTH
        )

        editBlacklistButton = ttk.Button(
            self,
            text = "Edit Blacklist",
            command = self.editBlacklistCallback,
            width=self.BUTTON_WIDTH
        )

        clearCachedFilesButton = ttk.Button(
            self,
            text = "Clear Cached Files",
            command = self.clearCachedFilesCallback,
            width=self.BUTTON_WIDTH
        )

        changeRootButton = ttk.Button(
            self,
            text = "Change Root",
            command = self.changeRootCallback,
            width=self.BUTTON_WIDTH
        )

        pfConsole = ttk.LabelFrame(
            self,
            text="Parsed Files",
            relief=tk.SUNKEN
        )
        
        pfConsoleContents = ttk.Label(
            pfConsole,
            justify=tk.LEFT,
            width = 40,
            font = (
                "Arial",
                10
            ),
            textvariable=self.pfConsoleTextVar
        )

        sfConsole = ttk.LabelFrame(
            self,
            text="Searched Files",
            relief=tk.SUNKEN
        )
        
        sfConsoleContents = ttk.Label(
            sfConsole,
            justify=tk.LEFT,
            width = 40,
            font = (
                "Arial",
                8
            ),
            textvariable=self.sfConsoleTextVar
        )

        autoParseLabel = ttk.Label(
            self,
            textvariable=self.autoParseLabelText,
            justify=tk.RIGHT
        )

        viewLogButton = ttk.Button(
            self,
            text="View Log",
            command = self.viewLogCallback,
            width=self.BUTTON_WIDTH
        )

        self.statusIndicator = ttk.Label(
            self,
            text="Idle",
            foreground=heading.cget("foreground"),
            padding = (20, 0)
            
        )

        currentRoot = ttk.Label(
            self,
            textvariable=self.currentRootTextVar,
            font = (
                "Arial",
                8
            )
        )

        # ----- Widgets Place -----

        heading.grid(
            row=0,
            column=0
        )

        parseNowButton.grid(
            row=1,
            column=0,
            padx=10,
            sticky="w"
        )

        editBlacklistButton.grid(
            row=2,
            column=0,
            padx=10,
            sticky="w"
        )

        clearCachedFilesButton.grid(
            row=3,
            column=0,
            padx=10,
            sticky="w"
        )

        changeRootButton.grid(
            row=4,
            column=0,
            padx=10,
            sticky="w"
        )

        viewLogButton.grid(
            row=6,
            column=1,
            padx=10,
            pady=10
        )

        pfConsole.grid(
            row=0,
            column=1,
            rowspan=6,
            padx=15,
            pady=8,
            sticky="ew"
        )

        pfConsoleContents.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        sfConsole.grid(
            row=0,
            column=2,
            rowspan=6,
            padx=15,
            pady=8,
            sticky="we"
        )

        sfConsoleContents.grid(
            row=0,
            column=0,
            sticky="we"
        )

        autoParseLabel.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=3
        )

        currentRoot.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=20,
            sticky='w'
        )

        self.statusIndicator.grid(
            row=6,
            column=2,
            padx=5,
            pady=20,
            sticky='e'
        )


        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        pfConsole.columnconfigure(0, weight=1)
        sfConsole.columnconfigure(0, weight=1)

    def parseNow(self) -> None:
        """Parse files now"""

        # Mark indicator active
        prevForeground = self.statusIndicator.cget("foreground")
        self.statusIndicator.config(text="Active", foreground="#F00")
        
        # Block Auto Parse
        wasBlocked = self.blockParse
        self.blockParse = True  # Stop two parse at once

        # Parse
        self.parserApp.parseAll(log=self.pfConsoleWrite, altLog=self.sfConsoleWrite)

        # Alive indicator status
        self.statusIndicator.config(text="Idle", foreground=prevForeground)

        # Reset block
        self.blockParse = wasBlocked  # Return to state when entered function

        # Update timer
        self.lastParse = datetime.now()

    def editBlacklistCallback(self) -> None:
        """Open blacklist file in OS text editor"""

        blklstFile = self.parserApp.parser.BLACKLIST_FILENAME

        if IS_WINDOWS:
            subprocess.Popen(["notepad.exe", blklstFile]) # Open blacklist file
        else:
            subprocess.Popen(["open", blklstFile, "-e"])


    def clearCachedFilesCallback(self) -> None:
        """Clear log of perviously parsed files."""
        self.pfConsoleWrite("~~Cleared File Cache~~")
        self.parserApp.clearLog()

    def changeRootCallback(self) -> None:
        """Prompt user to change root for tap search"""
        
        self.blockParse = True  # block parse for operation

        filename = filedialog.askdirectory()

        # Verify real path
        if os.path.exists(filename):
            self.parserApp.changeRoot(filename)
            self.currentRootTextVar.set(filename)
        elif filename == "":
            pass
        else:
            messagebox.showerror("G Code Editor Error", "Error: Cannot access specified root.")

        self.blockParse = False # unblock after complete

    def viewLogCallback(self) -> None:
        """Open log file in OS text editor"""

        if IS_WINDOWS:
            subprocess.Popen(["notepad.exe", self.parserApp.LOGFILE]) 
        else:
            subprocess.Popen(["open", self.parserApp.LOGFILE, "-e"])

    def pfConsoleWrite(self, text: str) -> None:
        """Write to parsed files console"""

        # limit number of lines
        if len(self.pfConsoleLines) > self.PFCONSOLE_MAX_LINES:
            self.pfConsoleLines.pop(0)

        # add new line to list
        self.pfConsoleLines.append(text)

        # place in tk var
        self.pfConsoleTextVar.set(
            "\n".join(self.pfConsoleLines)
        )

        # log in log file
        self.parserApp.fileLog(text)

        # print to terminal
        if DEBUG: print(f"PF CONSOLE: {text}")

    def sfConsoleWrite(self, text: str) -> None:
        """Write to searched files console."""

        # limit number of lines
        if len(self.sfConsoleLines) > self.SFCONSOLE_MAX_LINES:
            self.sfConsoleLines.pop(0)

        # add new line to list
        self.sfConsoleLines.append(text)

        # place in tk var
        self.sfConsoleTextVar.set(
            "\n".join(self.sfConsoleLines)
        )

        # print to terminal
        if DEBUG: print(f"SF CONSOLE: {text}")

        # force update
        self.sfConsoleRefreshCount += 1
        if self.sfConsoleRefreshCount % 15 == 0:
            self.update_idletasks()

    def countdown(self) -> None:
        """Runs every background refresh. Counts down until next auto parse."""

        deltaSeconds = (datetime.now() - self.lastParse).seconds
        timeUntil = self.AUTOPARSE_DELAY - deltaSeconds

        if timeUntil <= 0:
            self.parseNow()  # Parse

        self.autoParseLabelText.set(
            f"{timeUntil} seconds until next parse"
        )

    def backgroundRefresh(self) -> None:
        """Runs each second. Acts as a home for updating functions"""

        if not self.blockParse:
            self.countdown() # Only countdown when not blocked

        self.after(1000, self.backgroundRefresh)


if __name__ == "__main__":
    app = ParserGui()
    app.mainloop()