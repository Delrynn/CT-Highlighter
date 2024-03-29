﻿
# v0.7.0 CaseTrackerHighlights
# written by delryn@patton.pro

import os, shutil, datetime, re, argparse
import requests


parser = argparse.ArgumentParser(
    prog = 'CTHL_Installer',
    description = 'Installs FuelRats case highlights for CaseTracker in AdiIRC.',
    epilog = 'You read the help page. Good on you!',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-i', '--install', action='store_true', help='Triggers a (re)install of the tool.')
parser.add_argument('-u', '--uninstall', action='store_true', help='Triggers an uninstall of the tool. Ignored if -i is used.')
parser.add_argument('-d', '--debug', action='store_true', help='Writes new config files to the current directory, and leaves current configs in place.')
parser.add_argument('-c', '--configdir', action='store', help='If running as admin or a different user, use this to set a custom config directory path.\n(ex: -c "C:\Program Files\AdiIRC")')

args = parser.parse_args()


#CONSTANTLY CONSTANTS!
if args.configdir is None:
    CONFIG_DIR = os.getenv('LOCALAPPDATA') + '\\AdiIRC\\'
else: 
    CONFIG_DIR = str.strip(args.configdir, '"')

CTHL_SCRIPT_URL = 'https://raw.githubusercontent.com/Delrynn/CT-Highlighter/master/Templates/CT-Highlights-Template.ini'
HLDEF_URL = 'https://raw.githubusercontent.com/Delrynn/CT-Highlighter/master/Templates/highlightTemplate.txt'
DELIMS_URL = 'https://raw.githubusercontent.com/Delrynn/CT-Highlighter/master/Templates/delims.txt'

HIGHLIGHT_ENABLE_KEY = 'UseHighlight'
FLASHWHOLE_KEY = 'FlashWhole'
HIGHLIGHTS_DEFINE_SECTION = '[HighlightItems]'
SCRIPTS_SECTION = '[Scripts]'

CTHL_SCRIPT_FILENAME = 'CT-Highlights.ini'
CTHL_SCRIPT_TEMP_FILENAME = 'Templates\\CT-Highlights-Template.ini'
ADI_SCRIPT_PATH = CONFIG_DIR + '\\Scripts\\'

HLDEF_FILENAME = 'Templates\\highlightTemplate.txt'
CURRENT_HLDEF_FILENAME = 'curHL.txt'

ADI_CONFIG_FILEPATH = CONFIG_DIR + '\\config.ini'
NEW_CONFIG_FILENAME = 'newconfig.ini'

DELIMS_FILENAME = 'Templates\\delims.txt'
HIDDEN_CHAR = ''
DELIM = ''

def main():
    
    #debug skips writing files to the AppData directory, and skips deleting temporary files
    debugTest = args.debug

    if args.install or args.uninstall:
        log('Using Config file path: ' + ADI_CONFIG_FILEPATH)
        downloadTemplates()

        #AdiIRC uses some FUNKY characters
        #typing the characters in code causes the encoder to panic, so we read them from a file \o/
        with open(DELIMS_FILENAME, 'r') as temp:
            global HIDDEN_CHAR
            global DELIM 
            HIDDEN_CHAR = temp.read(1)
            DELIM = temp.read(1)

    #keep previous version of highlight template for cleanup purposes
    if not os.path.exists(CURRENT_HLDEF_FILENAME):
        shutil.copyfile(HLDEF_FILENAME, CURRENT_HLDEF_FILENAME)

    if args.install:
        install(debugTest)
    elif args.uninstall:
        uninstall(debugTest)
    else:
        print('-------------\nNo operation chosen. Please choose --install or --uninstall when executing program.\nMaybe read the documentation.\n¯\_(ツ)_/¯\n-------------')
        input('Press <Enter> to close...')

def log(message):
    #TODO: write to log file
    print (message)

def downloadTemplates():
    CTHL_Script_Template = requests.get(CTHL_SCRIPT_URL)
    HLDefs_Template = requests.get(HLDEF_URL)
    Delims = requests.get(DELIMS_URL)

    if CTHL_Script_Template.status_code not in range(200, 300) or \
       HLDefs_Template.status_code not in range(200, 300) or \
       Delims.status_code not in range(200, 300):
        print('Error: Could not download tempalte files from github.')
        exit(-4)


    try:
        if not os.path.exists('.\\Templates'):
            os.mkdir('.\\Templates')

        with open(CTHL_SCRIPT_TEMP_FILENAME, 'w', encoding="utf-8") as f:
            f.write(CTHL_Script_Template.text)
        with open(HLDEF_FILENAME, 'w', encoding="utf-8") as f:
            f.write(HLDefs_Template.text)
        with open(DELIMS_FILENAME, 'w', encoding="utf-8") as f:
            f.write(Delims.text)
    except:
        print('Error: Unable to write template files to .\Templates')
        exit(-3)

def install(debug):

    #all actual installs are re-installs
    if not debug:
        log('Performing uninstall first')
        uninstall(debug)


    
    #these numbers are used to align case numbers with highlight entry positions
    log('Writing new config')
    highlightsDone = False
    scriptsDone = False
    with open(ADI_CONFIG_FILEPATH, 'r') as ADIConf:
        with open(NEW_CONFIG_FILENAME, 'w') as newConf:
            for line in ADIConf:
                #Enable highlights if disabled
                if HIGHLIGHT_ENABLE_KEY in line:
                    log('Enabling highlights')
                    newConf.write('UseHighlight=True\n')

                #Disable entire line highlighting
                elif FLASHWHOLE_KEY in line:
                    newConf.write('FlashWhole=False\n')

                #find section with highlight definitions, add our highlights
                elif HIGHLIGHTS_DEFINE_SECTION in line:
                    highlightTotal, highlightOffset = addHighlights(ADIConf, newConf)
                    highlightsDone = True

                #handle scripts section, just add our CT-Highlights.ini script to the list
                elif SCRIPTS_SECTION in line:
                    addScript(ADIConf, newConf)
                    scriptsDone = True

                else:
                    newConf.write(line)
                    
                newConf.flush()

            if not highlightsDone:
                highlightTotal, highlightOffset = addHighlights(ADIConf, newConf, newSection=True)
                highlightsDone = True
                newConf.flush()

            if not scriptsDone:
                addScript(ADIConf, newConf, newSection=True)
                scriptsDone = True
                newConf.flush()

    #make a backup of the highlights to assist with uninstalling
    shutil.copyfile(HLDEF_FILENAME, CURRENT_HLDEF_FILENAME)
    
    #fill in variables in Adi script
    with open(CTHL_SCRIPT_TEMP_FILENAME, 'r') as CTScriptTemplate:
        with open(CTHL_SCRIPT_FILENAME, 'w') as CTScript:  
            data = CTScriptTemplate.read()
            data = data.replace('<OFFSET>', str(highlightOffset))
            data = data.replace('<TOTAL_HIGHLIGHTS>', str(highlightTotal))
            CTScript.write(data)
            CTScript.flush()
            CTScript.close()
            
    #write changes
    if not debug:
        shutil.copyfile(CTHL_SCRIPT_FILENAME, ADI_SCRIPT_PATH + CTHL_SCRIPT_FILENAME)
        shutil.copyfile(NEW_CONFIG_FILENAME, ADI_CONFIG_FILEPATH)
        os.remove(NEW_CONFIG_FILENAME)

    log('Installation complete')

def addHighlights(ADIConf, newConf, newSection=False):
    log('Updating highlights section')

    #gather case highlights
    caseHighlightsFile = open(HLDEF_FILENAME, 'r')
    caseHighlights = caseHighlightsFile.readlines()
    caseHighlightsFile.close()

    if newSection:
        newConf.write('\n\n[Highlight]\nUseHighlight=True\nFlashWhole=False\n\n')

    newConf.write(HIGHLIGHTS_DEFINE_SECTION + '\n') #write section header to new conf
    line = ADIConf.readline()
    highlightIndex=0;

    #go through the entire section, writing current highlights
    while line != '\n' and not line.startswith('[') and not newSection and line:
        newConf.write(line)
        highlightIndex+=1
        line = ADIConf.readline()
        newConf.flush()
                    
    highlightOffset = highlightIndex + 1
    #back up one step if needed
    if line == '\n':
        newConf.seek(newConf.tell()-1)
    elif not line:
        newConf.write('\n')
                        
    #back up, and insert the case number highlights
    log('Inserting case highlights')
    for highlight in caseHighlights:
        newConf.write('n' + str(highlightIndex) + '=' + highlight)
        highlightIndex+=1
                    
    #write whitespace and the header of the next section
    newConf.write('\n\n')
    if line.startswith('['):
        addScript(ADIConf, newConf)

    return len(caseHighlights), highlightOffset

def addScript(ADIConf, newConf, newSection=False):
    log('Updating Scripts section')
    newConf.write(SCRIPTS_SECTION + '\n') #write section header to new conf
    line = ADIConf.readline()
    scriptIndex = 0

    #print existing script files
    while line != '\n' and not line.startswith('[') and not newSection and line:
        newConf.write(line)
        line = ADIConf.readline()
        scriptIndex += 1 #i don't even know if these index numbers matter
    #insert our script
    if not line:
        newConf.write('\n')
    newConf.write('n' + str(scriptIndex) + '=.\\Scripts\\' + CTHL_SCRIPT_FILENAME + '\n')

    #if there wasn't whitespace between the sections, add it for nice formatting
    if line.startswith('['):
        newConf.write('\n')

    newConf.write(line)

def uninstall(debug):

    if not debug:
        #backup!
        now = datetime.datetime.now()
        try:
            shutil.copyfile(ADI_CONFIG_FILEPATH, ADI_CONFIG_FILEPATH + '.bak' + now.strftime('%Y%m%d-%H%M%S'))
        except:
            log('Problem backing up config.ini. Is the file somewhere other than ' + ADI_CONFIG_FILEPATH + '?')
            exit(-1)

    log('Removing previous CT highlights')
    try:
        with open(ADI_CONFIG_FILEPATH, 'r') as ADIConf:
            with open(NEW_CONFIG_FILENAME, 'w') as newConf:
                for line in ADIConf:
                    #remove our highlight entries
                    if HIGHLIGHTS_DEFINE_SECTION in line:
                        log('Cleaning Highlights Section')
                        removeHighlights(ADIConf, newConf)

                    #remove our script from the list of scripts
                    elif SCRIPTS_SECTION in line:
                        log('Cleaning Scripts Section')
                        removeScript(ADIConf, newConf)
                    
                    #nothing to do, just write the line as-is
                    else:
                        newConf.write(line)
    except:
        log('Problem writing new config.ini. Is the file somewhere other than ' + ADI_CONFIG_FILEPATH + '?')
        exit(-2)


    if not debug:
        #write changes
        shutil.copyfile(NEW_CONFIG_FILENAME, ADI_CONFIG_FILEPATH)
        #cleanup
        os.remove(NEW_CONFIG_FILENAME)
        if os.path.exists(ADI_SCRIPT_PATH + CTHL_SCRIPT_FILENAME):
            os.remove(ADI_SCRIPT_PATH + CTHL_SCRIPT_FILENAME)

    log('Uninstall complete')

def removeHighlights(ADIConf, newConf):
    newConf.write(HIGHLIGHTS_DEFINE_SECTION + '\n') #write section header to new conf
    line = ADIConf.readline()
    
    #gather highlight lines
    currentHighlightsFile = open(CURRENT_HLDEF_FILENAME, 'r')
    currentHighlights = currentHighlightsFile.readlines()
    currentHighlightsFile.close()
                    
    #gather up all of the highlights, and truncate the 'n#=' start
    highlightIndex = 0
    while line != '\n' and not line.startswith('['):
        lineSplit = line.split('=', 1)
        if len(lineSplit) == 2:
            matchFlag = False
            #see if the current highlight matches any of the case highlights to remove
            for highlight in currentHighlights:
                highlightRegex = regexifyHighlightLine(highlight)

                #if it's a case highlight, just skip it
                if re.search(highlightRegex, line):
                    matchFlag = True
                    break

            #if there were no matches, write the highlight back in
            if not matchFlag:
                newConf.write('n' + str(highlightIndex) + '=' + lineSplit[1])
                highlightIndex += 1
                        
        line = ADIConf.readline()
    newConf.write('\n')
    if line.startswith('['):
        removeScript(ADIConf, newConf)


def removeScript(ADIConf, newConf):
    newConf.write(SCRIPTS_SECTION + '\n') #write section header to new conf
    scriptIndex=0
    eraseFlag = True
    line = ADIConf.readline()
    while line != '\n' and not line.startswith('[') and line:
        lineSplit = line.split('=', 1)
        if len(lineSplit) == 2:
            if eraseFlag:
                if CTHL_SCRIPT_FILENAME not in line:
                    newConf.write('n' + str(scriptIndex) + '=' + lineSplit[1])
                    scriptIndex += 1
                else:
                    eraseFlag = False
            else:
                newConf.write('n' + str(scriptIndex) + '=' + lineSplit[1])
                scriptIndex += 1
        line = ADIConf.readline()
    
    #if there wasn't whitespace between the sections, add it for nice formatting
    if line.startswith('['):
        newConf.write('\n')

    newConf.write(line)


def regexifyHighlightLine(highlightLine):
    #replace color parameter with '\d*' for regex to match any color customizations
    lineSplit = str(highlightLine).split(DELIM)
    lineSplit[2]='\\d*'+HIDDEN_CHAR
    return DELIM.join(lineSplit)

if __name__=="__main__":
    main()