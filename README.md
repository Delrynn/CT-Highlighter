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

Assumes the user is using AdiIRC configurations stored in %localappdata% (ie. C:\Users\USERNAME\AppData\Local\AdiIRC). In other words, this will only work if you run AdiIRC as the current user, and not as another user or Administrator.

Assumes the user is sane, and is using a dark theme with a very dark or black MessageBox Background. Colors can be adjusted after installation. Light theme support comming soon™.

Assumes the user has not altered default mIRC Colors. Colors can be adjusted after installation.

The CaseTracker Highlights must be at the top of the highlight list.

Additional highlights beyond case #9 should be added via the highlightTemplate.txt file.

## Usage

Install/Uninstall:  
```
CT-Highlighter.exe <install|uninstall> [debug]
```

The install acts as a re-install if this utility has been used previously. The debug flag will write the new config.ini and CT-Highlights.ini files only to the current dir.

Highlight colors can be customized after installation using the in-program options menu.

Additional case highlights, for example highlighting beyond case #9, should be added by updating the highlightTemplate.txt file, and then running the install.

Additional generic highlights can be added/removed **BELOW** the case highlights.

If changes are made that shift the highlights up or down on the list, either uninstall the highlights first, or increase/decrease the %highlightOffset and %numOfHighlights vars (CT-Highlights.ini) by how many positions they shifted.

## TODO

- Support light theme with alternate color set
- Install CaseTracker™ if missing
- Implement --help
