# Idle-Tap-Editor

## Overview

A common issue with post-processors in the CAM environment is corruption across machines. While some machines will work perfectly fine with the post-processor at hand, others--often off-brand--will fail to execute the correct movements. 

#### Example 

`G28 G91 Z0.` is a homing sequence, meant to return home once a toolpath is completed. The error occurs with machines that don't have homing capabilities. This will result in an uncontrolled plunge into the workpiece, often causing terminate damage to the machine and a ruined part.


The solution is misleadingly simple; just remove the conflicting lines. 