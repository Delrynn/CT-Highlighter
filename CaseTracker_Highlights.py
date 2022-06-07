
from msilib.schema import File
import os, shutil, datetime, sys, re

def main():
    if not os.path.exists('.\\curHL.txt'):
        shutil.copyfile('.\\highlightTemplate.txt', '.\\curHL.txt')

    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'uninstall':
        uninstall()

def install():
    uninstall()
    appdatalocalPath = os.getenv('LOCALAPPDATA')

    #gather highlight lines
    caseHighlightsFile = open(".\\highlightTemplate.txt", 'r')
    caseHighlights = caseHighlightsFile.readlines()
    caseHighlightsFile.close()
    
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
                    highlightStartPos = newConf.tell() #note down starting pos for inserts
                    highlightList = list()

                    #gather up existing highlights
                    while line != '\n' or line.startswith('['):
                        lineSplit = line.split('=', 1)
                        if len(lineSplit) == 2:
                            highlightList.append(lineSplit[1])
                            newConf.write(line)
                        line = ADIConf.readline()

                    #back up, and insert the case number highlights
                    newConf.seek(highlightStartPos)
                    newConf.writelines(caseHighlights)
                    newConf.write('\n')

                    #write the old highlights back in
                    endIndex = len(caseHighlights)
                    for oldHighlight in highlightList:
                        oldHighlightLine = 'n' + str(endIndex) + '=' + oldHighlight
                        newConf.write(oldHighlightLine)
                        endIndex += 1

                    newConf.write('\n')

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

    #write changes
    shutil.copyfile('.\\CT-Highlights.ini', appdatalocalPath + '\\AdiIRC\\Scripts\\CT-Highlights.ini')
    shutil.copyfile(appdatalocalPath + '\\AdiIRC\\newconfig.ini', appdatalocalPath + '\\AdiIRC\\config.ini')
    #cleanup
    os.remove(appdatalocalPath + '\\AdiIRC\\newconfig.ini')

def uninstall():
    appdatalocalPath = os.getenv('LOCALAPPDATA')

    #backup!
    now = datetime.datetime.now()
    shutil.copyfile(appdatalocalPath + '\\AdiIRC\\config.ini', appdatalocalPath + '\\AdiIRC\\config.ini.bak.' + now.strftime('%Y%m%d-%H%M%S'))

    #gather highlight lines
    currentHighlightsFile = open(".\\curHL.txt", 'r')
    currentHighlights = currentHighlightsFile.readlines()
    currentHighlightsFile.close()

    currentHighlightsSplit = list()
    for highlight in currentHighlights:
        currentHighlightsSplit.append(highlight.split('=', 1)[1])

    with open(appdatalocalPath + '\\AdiIRC\\config.ini', 'r') as ADIConf:
        with open(appdatalocalPath + '\\AdiIRC\\newconfig.ini', 'w') as newConf:
            for line in ADIConf:
                if '[HighlightItems]' in line:
                    newConf.write(line) #write section header to new conf
                    line = ADIConf.readline()

                    #gather up existing highlights
                    highlightIndex = 0
                    eraseFlag = True
                    while line != '\n' or line.startswith('['):
                        lineSplit = line.split('=', 1)
                        if len(lineSplit) == 2:
                            #check if we're done deleting highlights
                            if highlightIndex >= len(currentHighlightsSplit):
                                eraseFlag = False
                                highlightIndex = 0
                                newConf.write('n' + str(highlightIndex) + '=' + lineSplit[1])
                            
                            #check if highlight matches template
                            elif eraseFlag:
                                matchFlag = False
                                for highlight in currentHighlightsSplit:
                                    highlightRegex = regexifyHighlightLine(highlight)
                                    if re.search(highlightRegex, line):
                                        matchFlag = True

                                if not matchFlag:
                                    newConf.write('n' + str(highlightIndex) + '=' + lineSplit[1])

                            #done cleaning up, just write the rest
                            else:
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