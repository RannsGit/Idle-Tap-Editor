# Idle-Tap-Editor

## Overview

A common issue with post-processors in the CAM environment is corruption across machines. While some machines will work perfectly fine with the post-processor at hand, others--often off-brand--will fail to execute the correct movements. 

#### Example 

`G28 G91 Z0.` is a homing sequence meant to return home once a toolpath is completed. The error occurs with machines that don't have homing capabilities. This will result in an uncontrolled plunge into the workpiece, often causing terminate damage to the machine and a ruined part.


The solution is misleadingly simple; just remove the conflicting lines. `blacklist.txt` is where all the blacklisted lines (lines to be removed) are stored.

##Usage

1. Load `blacklist.txt` with all the gcode commands you would like to remove.
2. Call `starter.bat` with your target directory. For example: `starter.bat \\Users\\johndoe\\desktop`
 - Because this program targets every file in every sub-directory of the given directory, make sure to carefully select the root in which you would like to use. 

