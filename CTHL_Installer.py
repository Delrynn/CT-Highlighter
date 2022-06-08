
# v0.2.0 CaseTrackerHighlights
# written by delryn@patton.pro

from msilib.schema import File
import os, shutil, datetime, sys, re

def main():
    #keep previous version of highlight template for cleanup purposes
    if not os.path.exists('.\\curHL.txt'):
        shutil.copyfile('.\\highlightTemplate.txt', '.\\curHL.txt')

    debugTest = False
    if len(sys.argv) > 2 and sys.argv[2] == 'debug':
        debugTest = True

    if sys.argv[1] == 'install':
        install(debugTest)
    elif sys.argv[1] == 'uninstall':
        uninstall(debugTest)

def install(debug):

    if not debug:
        uninstall(debug)

    appdatalocalPath = os.getenv('LOCALAPPDATA')

    #gather highlight lines
    caseHighlightsFile = open(".\\highlightTemplate.txt", 'r')
    caseHighlights = caseHighlightsFile.readlines()
    caseHighlightsFile.close()
    
    highlightTotal = len(caseHighlights)
    highlightOffset = 1
    with open(appdatalocalPath + '\\AdiIRC\\config.ini', 'r') as ADIConf:
        with open(appdatalocalPath + '\\AdiIRC\\newconfig.ini', 'w') as newConf:
            for line in ADIConf:
                #Enable highlights if disabled
                if 'UseHighlight=False' in line:
                    newConf.write('UseHighlight=True\n')

                #find section with highlight definitions
                elif '[HighlightItems]' in line:
                    newConf.write(line) #write section header to new conf
                    line = ADIConf.readline()
                    highlightIndex=0;

                    while line != '\n' and not line.startswith('['):
                        newConf.write(line)
                        highlightIndex+=1
                        line = ADIConf.readline()
                        newConf.flush()
                    
                    highlightOffset = highlightIndex + 1
                    highlightStartPos = newConf.tell()
                    if line == '\n':
                        newConf.seek(highlightStartPos-1)


                    #back up, and insert the case number highlights
                    for highlight in caseHighlights:
                        newConf.write('n' + str(highlightIndex) + '=' + highlight)
                        highlightIndex+=1
                    

                    newConf.write('\n\n')
                    if line.startswith('['):
                        newConf.write(line)

                elif '[Scripts]' in line:
                    newConf.write(line) #write section header to new conf
                    line = ADIConf.readline()
                    scriptIndex = 0
                    while line != '\n':
                        newConf.write(line)
                        line = ADIConf.readline()
                        scriptIndex += 1
                    newConf.write('n' + str(scriptIndex) + '=.\\Scripts\\CT-Highlights.ini\n\n')

                else:
                    newConf.write(line)

    shutil.copyfile('.\\highlightTemplate.txt', '.\\curHL.txt')
    
    #fill in variables in Adi script
    with open('.\\CT-Highlights-Template.ini', 'r') as CTScriptTemplate:
        with open('.\\CT-Highlights.ini', 'w') as CTScript:  
            data = CTScriptTemplate.read()
            data = data.replace('<OFFSET>', str(highlightOffset))
            data = data.replace('<TOTAL_HIGHLIGHTS>', str(highlightTotal))
            CTScript.write(data)
            CTScript.flush()
            CTScript.close()
            
    #write changes
    if not debug:
        shutil.copyfile('.\\CT-Highlights.ini', appdatalocalPath + '\\AdiIRC\\Scripts\\CT-Highlights.ini')
        shutil.copyfile(appdatalocalPath + '\\AdiIRC\\newconfig.ini', appdatalocalPath + '\\AdiIRC\\config.ini')
        os.remove(appdatalocalPath + '\\AdiIRC\\newconfig.ini')

def uninstall(debug):
    appdatalocalPath = os.getenv('LOCALAPPDATA')

    if not debug:
        #backup!
        now = datetime.datetime.now()
        shutil.copyfile(appdatalocalPath + '\\AdiIRC\\config.ini', appdatalocalPath + '\\AdiIRC\\config.ini.bak.' + now.strftime('%Y%m%d-%H%M%S'))

    #gather highlight lines
    currentHighlightsFile = open(".\\curHL.txt", 'r')
    currentHighlights = currentHighlightsFile.readlines()
    currentHighlightsFile.close()

    with open(appdatalocalPath + '\\AdiIRC\\config.ini', 'r') as ADIConf:
        with open(appdatalocalPath + '\\AdiIRC\\newconfig.ini', 'w') as newConf:
            for line in ADIConf:
                if '[HighlightItems]' in line:
                    newConf.write(line) #write section header to new conf
                    line = ADIConf.readline()

                    #gather up existing highlights
                    highlightIndex = 0
                    while line != '\n' or line.startswith('['):
                        lineSplit = line.split('=', 1)
                        if len(lineSplit) == 2:

                                matchFlag = False
                                for highlight in currentHighlights:
                                    highlightRegex = regexifyHighlightLine(highlight)
                                    if re.search(highlightRegex, line):
                                        matchFlag = True
                                        break

                                if not matchFlag:
                                    newConf.write('n' + str(highlightIndex) + '=' + lineSplit[1])
                                    highlightIndex += 1
                        
                        line = ADIConf.readline()
                    newConf.write('\n')

                elif '[Scripts]' in line:
                    newConf.write(line) #write section header to new conf
                    scriptIndex=0
                    eraseFlag = True
                    while line != '\n':
                        lineSplit = line.split('=', 1)
                        if len(lineSplit) == 2:
                            if eraseFlag:
                                if 'CT-Highlights.ini' not in line:
                                    newConf.write('n' + str(scriptIndex) + '=' + lineSplit[1])
                                else:
                                    scriptIndex -= 1
                            else:
                                newConf.write('n' + str(scriptIndex) + '=' + lineSplit[1])
                        scriptIndex += 1
                        line = ADIConf.readline()
                    newConf.write('\n')

                else:
                    newConf.write(line)
    


    if not debug:
        #write changes
        shutil.copyfile(appdatalocalPath + '\\AdiIRC\\newconfig.ini', appdatalocalPath + '\\AdiIRC\\config.ini')
        #cleanup
        os.remove(appdatalocalPath + '\\AdiIRC\\newconfig.ini')
        if os.path.exists(appdatalocalPath + '\\AdiIRC\\Scripts\\CT-Highlights.ini'):
            os.remove(appdatalocalPath + '\\AdiIRC\\Scripts\\CT-Highlights.ini')

def regexifyHighlightLine(highlightLine):
    hiddenChar = highlightLine[5]
    delim = highlightLine[6]
    lineSplit = str(highlightLine).split(delim)
    lineSplit[2]='\\d*'+hiddenChar
    return delim.join(lineSplit)

if __name__=="__main__":
    main()