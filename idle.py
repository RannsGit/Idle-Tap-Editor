import sys 
import subprocess
import time
import locator

DELAY_TIME = 10 #Time between updates
def main():
    print(f"Targeting {DIRECTORY}.")
    while 1:
        cmd = [sys.executable, "header_mod.py",r'"{}"'.format(argv[1])]
        subprocess.call(cmd, shell=True)
        time.sleep(DELAY_TIME)

if __name__ == "__main__":
    main()