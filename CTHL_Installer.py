
# v0.4.1 CaseTrackerHighlights
# written by delryn@patton.pro

from msilib.schema import File
import os, shutil, datetime, sys, re

#CONSTANTLY CONSTANTS!
APPDATALOCAL_PATH = os.getenv('LOCALAPPDATA')

HIGHLIGHT_ENABLE_KEY = 'UseHighlight'
HIGHLIGHTS_DEFINE_SECTION = '[HighlightItems]'
SCRIPTS_SECTION = '[Scripts]'

CTHL_SCRIPT_FILENAME = 'CT-Highlights.ini'
CTHL_SCRIPT_TEMP_FILENAME = 'CT-Highlights-Template.ini'
ADI_SCRIPT_PATH = APPDATALOCAL_PATH + '\\AdiIRC\\Scripts\\'

HLDEF_FILENAME = 'highlightTemplate.txt'
CURRENT_HLDEF_FILENAME = 'curHL.txt'

ADI_CONFIG_FILEPATH = APPDATALOCAL_PATH + '\\AdiIRC\\config.ini'
NEW_CONFIG_FILENAME = 'newconfig.ini'

DELIMS_FILENAME = 'delims.txt'

def main():
    #keep previous version of highlight template for cleanup purposes
    if not os.path.exists('CURRENT_HLDEF_FILENAME'):
        shutil.copyfile(HLDEF_FILENAME, CURRENT_HLDEF_FILENAME)

    #debug skips writing files to the AppData directory, and skips deleting temporary files
    debugTest = False
    if len(sys.argv) > 2 and sys.argv[2] == 'debug':
        debugTest = True

    if sys.argv[1] == 'install':
        install(debugTest)
    elif sys.argv[1] == 'uninstall':
        uninstall(debugTest)

def log(message):
    #TODO: write to log file
    print (message)

def install(debug):

    #all actual installs are re-installs
    if not debug:
        log('Performing uninstall first')
        uninstall(debug)


    
    #these numbers are used to align case numbers with highlight entry positions
    log('Writing new config')
    with open(ADI_CONFIG_FILEPATH, 'r') as ADIConf:
        with open(NEW_CONFIG_FILENAME, 'w') as newConf:
            for line in ADIConf:
                #Enable highlights if disabled
                if HIGHLIGHT_ENABLE_KEY in line:
                    log('Enabling highlights')
                    newConf.write('UseHighlight=True\n')

                #find section with highlight definitions, add our highlights
                elif HIGHLIGHTS_DEFINE_SECTION in line:
                    highlightTotal, highlightOffset = addHighlights(ADIConf, newConf)

                #handle scripts section, just add our CT-Highlights.ini script to the list
                elif SCRIPTS_SECTION in line:
                    addScript(ADIConf, newConf)

                else:
                    newConf.write(line)
                    
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

def addHighlights(ADIConf, newConf):
    log('Updating highlights section')

    #gather case highlights
    caseHighlightsFile = open(HLDEF_FILENAME, 'r')
    caseHighlights = caseHighlightsFile.readlines()
    caseHighlightsFile.close()

    newConf.write(HIGHLIGHTS_DEFINE_SECTION + '\n') #write section header to new conf
    line = ADIConf.readline()
    highlightIndex=0;

    #go through the entire section, writing current highlights
    while line != '\n' and not line.startswith('['):
        newConf.write(line)
        highlightIndex+=1
        line = ADIConf.readline()
        newConf.flush()
                    
    highlightOffset = highlightIndex + 1
    #back up one step if needed
    if line == '\n':
        newConf.seek(newConf.tell()-1)
                        
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

def addScript(ADIConf, newConf):
    log('Updating Scripts section')
    newConf.write(SCRIPTS_SECTION + '\n') #write section header to new conf
    line = ADIConf.readline()
    scriptIndex = 0

    #print existing script files
    while line != '\n' and not line.startswith('['):
        newConf.write(line)
        line = ADIConf.readline()
        scriptIndex += 1 #i don't even know if these index numbers matter
    #insert our script
    newConf.write('n' + str(scriptIndex) + '=.\\Scripts\\' + CTHL_SCRIPT_FILENAME + '\n')

    #if there wasn't whitespace between the sections, add it for nice formatting
    if line.startswith('['):
        newConf.write('\n')

    newConf.write(line)

def uninstall(debug):

    if not debug:
        #backup!
        now = datetime.datetime.now()
        shutil.copyfile(ADI_CONFIG_FILEPATH, ADI_CONFIG_FILEPATH + '.bak' + now.strftime('%Y%m%d-%H%M%S'))

    log('Removing previous CT highlights')
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
    while line != '\n' and not line.startswith('['):
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


#AdiIRC uses some FUNKY characters
#typing the characters in code causes the encoder to panic, so we read them from a file \o/
with open(DELIMS_FILENAME, 'r') as temp:
    HIDDEN_CHAR = temp.read(1)
    DELIM = temp.read(1)

def regexifyHighlightLine(highlightLine):
    #replace color parameter with '\d*' for regex to match any color customizations
    lineSplit = str(highlightLine).split(DELIM)
    lineSplit[2]='\\d*'+HIDDEN_CHAR
    return DELIM.join(lineSplit)

if __name__=="__main__":
    main()