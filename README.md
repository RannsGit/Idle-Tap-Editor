# Idle-Tap-Editor

## Overview

A common issue with post-processors in the CAM environment is corruption across machines. Often, offbrand machines will have half-compatable hardware which can easily misinterpret lines of gcode. To fix this, this program automatically scans for all .tap files in a specified root directory, and modifies them to remove any blacklisted commands.

#### Example 

`G28 G91 Z0.` is a homing sequence meant to return home once a toolpath is completed. The error occurs with machines that don't have homing capabilities; some machines will unexpectedly plunge, breaking the tool and damaging the part.


The solution is misleadingly simple; just remove the conflicting lines. `blacklist.txt` is where all the blacklisted lines (lines to be removed) are stored (each deliniated by newlines).

## Usage

1. Run the `.pyc` program
2. Edit blacklisted lines
3. Specify root
4. Program will parse every 30 seconds, or you can parse immedietly, manually.


