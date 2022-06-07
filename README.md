# CaseTracker-Highlights

The point of this utility is to easily enable and disable an addon to LittleFool's CaseTracker™. The addon uses the CaseTracker™ to identify messages from clients in any FuelRats #channel, add their case number to the beginning of the line, and highlight the entire line in a case-matching color.

Example:

![Highlighting example](/Images/example.png)

## Prerequisites

![AdiIRC](https://adiirc.com/) v4+  
![LittleFool's CaseTracker™](https://github.com/LittleFool/fuelrats-casetracker)

Assumption:  
User is using AdiIRC configurations stored in %localappdata% (ie. C:\Users\USERNAME\AppData\Local\AdiIRC). In other words, this will only work if you run AdiIRC as the current user, and not as another user or Administrator.

## Install/Uninstall

Usage:  
python.exe .\CaseTracker_Highlights.py install  
python.exe .\CaseTracker_Highlights.py uninstall

## TODO

- Support light theme
- Install CaseTracker™ if missing
