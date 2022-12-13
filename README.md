# CaseTracker-Highlighter

The point of this utility is to easily enable and disable an addon to LittleFool's CaseTracker™. The addon uses the CaseTracker™ to identify messages from clients in any FuelRats #channel, add their case number to the beginning of the line, and highlight the entire line in a case-matching color.

Example:

![Highlighting example](/Images/example.png)

## Prerequisites

![AdiIRC](https://adiirc.com/) v4+  
![LittleFool's CaseTracker™](https://github.com/LittleFool/fuelrats-casetracker)

## Features

- Identifies messages sent by clients
- Prepends case number to client message
- Highlights client message line with colors matching their case number
- Customizable colors

## Assumptions and Limitations

The default configuration directory is %localappdata% (ie. C:\Users\USERNAME\AppData\Local\AdiIRC). 
If you are running AdiIRC as an Administrator, or otherwise using a different configuration directory,
use the -c/--configdir flag to change the target AdiIRC config directory (ie. C:\Program Files\AdiIRC)

Assumes the user is sane, and is using a dark theme with a very dark or black MessageBox Background. 
Colors can be adjusted after installation if needed through the in-app highlight or color options page. Light theme support comming soon™.

Assumes the user has not altered default mIRC Colors. Altering the colors may make the highlights illegible.
Colors can be adjusted after installation if needed through the in-app highlight or color options page.

Additional case highlights beyond case #9 should be added via the highlightTemplate.txt file and reinstallation.

Additional generic highlights should be added **BELOW** the case highlights. If you need to add high priority generic highlights,
uninstall this first, then reinstall it afterward. 

## Usage

 
```
usage: CTHL_Installer [-h] [-i] [-u] [-d] [-c CONFIGDIR]

Installs FuelRats case highlights for CaseTracker in AdiIRC.

options:
  -h, --help            show this help message and exit
  -i, --install         Triggers a (re)install of the tool.
  -u, --uninstall       Triggers an uninstall of the tool. Ignored if -i is used.
  -d, --debug           Writes new config files to the current directory, and leaves current configs in place.
  -c CONFIGDIR, --configdir CONFIGDIR
                        If running as admin or a different user, use this to set a custom config directory path.
                        (ex: -c "C:\Program Files\AdiIRC")

```

Example default install:  
![Install example](/Images/install.png)

Example custom conf directory install:  
![Install example](/Images/install.png)

Restart AdiIRC if it is currently running after the install.

The install acts as a re-install if this utility has been used previously. The debug flag will 
write the new config.ini and CT-Highlights.ini files only to the current dir.

Highlight colors can be customized after installation using the in-program options menu.

Additional case highlights, for example highlighting beyond case #9, should be added by updating 
the highlightTemplate.txt file, and then running the reinstall.

Additional generic highlights can be added/removed **BELOW** the case highlights.

If changes are made that shift the highlights up or down on the list, either uninstall the 
highlights first, or increase/decrease the %highlightOffset and %numOfHighlights vars 
(CT-Highlights.ini) by how many positions they shifted.

## TODO

- Support light theme with alternate color set
- Install CaseTracker™ if missing
