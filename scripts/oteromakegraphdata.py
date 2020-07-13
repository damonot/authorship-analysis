# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 20:51:17 2019

@author: damon
"""
import scripts.oterogetrepo as getrep # download git repos
import scripts.oteromakelynksoft as makelynks
import scripts.oteroanalyzegraphs as anlyzgrf
from itertools import islice # csv iteration
import csv, subprocess, os # bash
import pandas as pd
import os.path
import unicodedata


# converts windows path system to bash-readable format
def fix_path(path):
    newPath = path.replace(os.path.sep, '/') # switch \ to /
    newPath = newPath[0].lower() + newPath[1:] # make drive lowercase C: -> c:
    newPath = newPath.replace(':','') # delete : from drive
    if(newPath[0] != '/'): # if it's already formatted to UX path, don't add another '/'
        finalPath = '/' + newPath # add / to beginning of path
    
    return finalPath

# FEATURE EXTRACTION: find author of the given error
def analyze_auth(authorErrorInput, authorErrorOutput, cwd, repoBashPath, errorType):
    print('\nStarting '+errorType+' analysis...', end = '')
    doAnalyze = 'y'    

    # has the author-error .txt already been generated?
    if(os.path.isfile(authorErrorOutput)):
            doAnalyze = input('It appears author '+errorType+' analysis has already been conducted.'+
                      ' Re-analyze '+repoBashPath+'? [y]/n\n')
    else:
        print('No prior analysis file found. Reading CSV now...')
    
    # generate author-error from raw SonarQube CSV
    authErrorOut = authorErrorOutput # stops weird udf error
    if(doAnalyze == 'y'):
        get_auths_from_csv(authorErrorInput, cwd, repoBashPath, errorType, authErrorOut)

# DATA CLEANING: generate text file of author-file pairs
def get_auths_from_csv(CSV, cwd, repoBashPath, errorType, outputFile):
    csvLoc =  cwd + '\\'+ CSV # absolute path to csv file
    cwdBash = fix_path(cwd) # reformats for bash conventions
    script = cwd + '\\otero-AuthorFinder.sh'
    
    with open(csvLoc) as fd: # iterate through sonarQube import CSV
        for row in islice(csv.reader(fd), 1, None): # skips header
            fileBashPath = cwdBash + '/' + row[0] # bashformatted path to file
            badLine = row[2] # line of file with flaw
            description = row[1] # description of flaw
            errorRule = row[4] # TODO subsititute rule with desc
            # calls AuthorFinder.sh to find author of vulnerable code snippits
            subprocess.run([script, repoBashPath, fileBashPath, badLine, errorType, errorRule, outputFile], shell=True)

# connects authors that have contributed to the same file
def connect_coworkers(inputFiles, outputFile):
    lineList = []
    
    #for file in inputFiles:    
    with open(inputFiles, encoding='utf-8') as file:
        for line in file:
            #print(line)
            fields = line.split() # line: author, file
            lineList.append([fields[0], fields[1]])
    
    connectedAuths = []
    
    for line in lineList:
        auth = line[0]
        badFile = line[1]
        for compLine in lineList[:]:
            if(auth == compLine[0]): # skips author connected to itself
                continue
            if(badFile == compLine[1]): # common file found?    
                connection = [auth, compLine[0]] # yes, save authors
                revConnection = [connection[1], connection[0]]
                if((connection not in connectedAuths) and
                   (revConnection not in connectedAuths)):
                    connectedAuths.append(connection) # connect authors and save
    
    with open(outputFile, "w", encoding='utf-8') as output:
        for conxn in connectedAuths:
                output.write(str(conxn[0]) + '\t' +str(conxn[1]) + '\tcoworkers\n')


#connect bugs to vulns
def connect_flaws(flawsList, outputFile, repo, holder):
    bugsFile = flawsList[0]
    vulnsFile = flawsList[1]
    if(holder == "AUTHOR"):
        holderIndex = 0
    elif(holder == "FILE"):
        holderIndex = 1
    else:
        print("Holder Type Not Recognized.")
        quit()

    '''structure is...
    list: tups
        tup: vuln, dict
            dict: bug, count '''
    vulns = {}
    flawedFiles = []
    vulnfilepairs = []
    with open(vulnsFile, encoding='utf-8') as file:
        for line in file:
            fields = line.split()
            vulnHolder = fields[holderIndex]
            vulnRule = fields[4]
            pair = (vulnRule, vulnHolder)
            if pair not in vulns:
                vulns[pair] = 1
            else:
                vulns[pair] +=1
            #if(pair not in vulnfilepairs):
            #    vulnfilepairs.append[pair]


    vuln2bugs = []
    for pair in vulns:
        basebugDict = count_bugs(pair, bugsFile, holderIndex)
        #print(basebugDict)
        scaledbugDict = mult_bugs(vulns[pair], basebugDict)
        #TODO combine bug entries of same rule from diff files (put this funciton in anlyzgrf) 
        vuln2bugs.append(("V-"+vulnRule, scaledbugDict))
    

    #TODO adapt ffiaf2excel function OR adapt data structure
    anlyzgrf.ffiaf2excel(vuln2bugs, repo, holder)

def mult_bugs(vulnCount, bugDict):
    print(vulnCount)
    for key in bugDict.keys():
        bugDict[key] *= vulnCount
    return bugDict

def count_bugs(vulnfiletup, bugsFile, holderIndex):
    print(vulnfiletup[1]) # file
    vulnFile = vulnfiletup[1]
    with open(bugsFile, encoding='utf-8') as file:
        bugsofvuln = {}
        for line in file:
            fields = line.split()
            bugFile = fields[holderIndex]
            bugRule = fields[4]
            if bugFile == vulnFile:
                if bugRule not in bugsofvuln:
                    bugsofvuln[bugRule] = 1
                else:
                    bugsofvuln[bugRule] +=1 

    return bugsofvuln


# Degree Correlation Assortativity
def dca(flawsFile, repo, holder):
    if(holder == "AUTHOR"):
        holderIndex = 0
        xlOut = 'xl_data\\otero-'+repo+'-authDCA.xlsx'
    elif(holder == "FILE"):
        xlOut = 'xl_data\\otero-'+repo+'-fileDCA.xlsx'
        holderIndex = 1
    else:
        print("Holder Type Not Recognized.")
        xlOut = ''
        quit()

    degrees = {}
    with open(flawsFile, encoding='utf-8') as file:
        for line in file:
            fields = line.split()
            holder = fields[holderIndex]
            if holder not in degrees:
                degrees[holder] = 1
            else:
                degrees[holder] +=1

    dict2xl(degrees, xlOut)

    #print(degrees)
    for key in degrees:
        print(key+": "+str(degrees[key]))

def dict2xl(dict, xlOut):
    df = pd.DataFrame(data=dict, index=[0])
    df = (df.T)
    print (df)
    df.to_excel(xlOut)


# connects bad files which have the same author
def connect_flawedFiles(flawedFile, outputFile):
    lineList = []
    with open(flawedFile, encoding='utf-8') as file:
        for line in file:
            #print(line)
            fields = line.split()
            if(len(fields) < 2):
                continue
            lineList.append([fields[0], fields[1], fields[2]])
            
    #for line in lineList:
       # print(line)

    connectedFiles = []
    
    for line in lineList:
        #print(line)
        auth = line[0]
        badFile = line[1]
        errorType = line[2]
        for compLine in lineList[:]:
            if(badFile == compLine[1]): # skips file connected to itself
                continue
            if(auth == compLine[0]): # common file found?    
                connection = [badFile, compLine[1]] # yes, save files
                revConnection = [connection[1], connection[0]]
                if((connection not in connectedFiles) and
                   (revConnection not in connectedFiles)):
                    conxnType = str(errorType)
                    
                    connection.append(conxnType)
                    connectedFiles.append(connection) # connect authors and save

    with open(outputFile, "w", encoding='utf-8') as output:
        for conxn in connectedFiles:
                output.write(str(conxn[0]) + '\t' + str(conxn[1]) + '\t'+ str(conxn[2]) + '\n')         

# Merges a list of files into 1 file
def merge_files(fileList, outputFile):
    response = 'y'
    if(os.path.isfile(outputFile)):
        response = input("Merge has already been conducted. Overwrite " + outputFile+"? [y]/n\n")
        
    if(response == 'y'):
        with open(outputFile, 'w', encoding='utf-8') as outfile:
            for fname in fileList:
                if(os.path.isfile(fname)):
                    with open(fname, encoding='utf-8') as infile:
                        for line in infile:
                            outfile.write(line)
                if(os.path.isfile(fname)): # delete files after merged
                    response = input('Delete un-merged file '+fname+'? [y]/n\n')
                    if(response == 'y'):
                        os.remove(fname)        

def runner(repoAddress):
    print('Before running this program please conduct analysis using SonarQube'
          +' and export the results.\n')

    # Download Repo
    folderName = repoAddress.rsplit('/', 1)[-1] # last part of gitURL
    #getrep.download(repoAddress)
    
    # Path data for analysis steps
    cwd = os.getcwd()
    repoPath = cwd + '\\'+folderName    
    repoBashPath = fix_path(repoPath)            
    
    response = input('Has SonarQube analysis already been conducted on '+folderName+' data?\n'+
                     '[y]/n\n')
    
    
    if(response == 'y'):
        

        # Vulnerablity Analysis    
        vulnCSV = 'raw_data\otero-'+folderName+'-vuln.csv' # formerly authVulnInput
        authorVulnFilesOutput='text_data\otero-'+folderName+'-auth2vuln.txt' # file output by bash
        response = input('Perform Auth2Vuln Analysis? [y]/n\n')
        if(response == 'y'):
            analyze_auth(vulnCSV, authorVulnFilesOutput, cwd, repoBashPath, "vuln")
        
        
        # Bug Analysis       
        bugCSV ='raw_data\otero-'+folderName+'-bug.csv' # formerly authorBugInput
        authorBuggyFilesOutput='text_data\otero-'+folderName+'-auth2bug.txt' # file output by bash
        response = input('Perform Auth2Bug Analysis? [y]/n\n')
        if(response == 'y'):
            analyze_auth(bugCSV, authorBuggyFilesOutput, cwd, repoBashPath, "bug")
       
        # Merge vulnFiles with buggyFiles
        fileList = [authorVulnFilesOutput, authorBuggyFilesOutput]  
        auth2flawedFiles = 'text_data\otero-'+folderName+'-auth2flawedFiles.txt'
        merge_files(fileList, auth2flawedFiles) # fileList in -> auth2flawed out

         #TODO flaw-flaw network
        # flaw2flaw Analysis
        flaws = [
            'text_data\otero-'+folderName+'-auth2bug.txt','text_data\otero-'+folderName+'-auth2vuln.txt']
        print('\nStarting Flaw-Connectivity Analysis...', end = '')
        bug2vulnOutput = 'text_data\otero-'+folderName+'-flaw2flaw.txt' # flawA flawB commonAuth
        response = input('Perform bug2vuln Analysis by AUTHOR? [y]/n\n')
        if(response == 'y'):
            connect_flaws(flaws, bug2vulnOutput, folderName, "AUTHOR")
        response = input('Perform bug2vuln Analysis by FILE? [y]/n\n')
        if(response == 'y'):
            connect_flaws(flaws, bug2vulnOutput, folderName, "FILE")



        # DCA per repo 
        flawedFile = 'text_data\otero-'+folderName+'-auth2flawedFiles.txt'
        print('\nStarting Flaw-Connectivity Analysis...', end = '')
        response = input('Perform DCA Analysis by AUTHOR? [y]/n\n')
        if(response == 'y'):
            dca(flawedFile, folderName, "AUTHOR")
        response = input('Perform DCA Analysis by FILE? [y]/n\n')
        if(response == 'y'):
            dca(flawedFile, folderName, "FILE")
            

        #TODO convery connect_flaws output to lynksoft format 
        columnTypes = ['document', 'document'] # left column type, right column type
        response = input("Generate File-File Lynsoft XLSX for "+folderName+"? [y]/n\n")
        XLSXoutput = 'xl_data\lynks\oterolynks-'+folderName+'-flaws.xlsx'
        if(response == "y"):
            makelynks.genXLSX(bug2vulnOutput, columnTypes, XLSXoutput)

        #auth2Flaw Analysis
        response = input('Connect Authors To Flaws & Generate Lynksoft XLSX? [y]/n\n...')
        columnTypes = ['person', 'flag']
        XLSXoutput = 'xl_data\lynks\oterolynks-'+folderName+'-auth2flaws.xlsx'
        if(response == 'y'):
            makelynks.genXLSX(auth2flawedFiles, columnTypes, XLSXoutput)
        
        
        # auth2flawedFile Analysis
        print('\nStarting Author-Flawed File Analysis...', end = '')
        columnTypes = ['person', 'document'] # left column type, right column type
        response = input("Generate Author2FlawedFiles Lynsoft XLSX for "+folderName+"? [y]/n\n")
        XLSXoutput = 'xl_data\lynks\oterolynks-'+folderName+'-auth2flawedfiles.xlsx'
        if(response == "y"):
            makelynks.genXLSX(auth2flawedFiles, columnTypes, XLSXoutput)
        
        # Auth-Auth Analysis
        print('\nStarting Coworker Analysis...', end = '')
        coworkersOutput = 'text_data\otero-'+folderName+'-coworkers.txt'
        connect_coworkers(auth2flawedFiles, coworkersOutput)        
        columnTypes = ['person', 'person'] # left column type, right column type
        response = input("Generate Author-Author Lynsoft XLSX for "+folderName+"? [y]/n\n")
        XLSXoutput = 'xl_data\lynks\oterolynks-'+folderName+'-coworkers.xlsx'
        if(response == "y"):
            makelynks.genXLSX(coworkersOutput, columnTypes, XLSXoutput)
        
        
        # File-File Analysis
        print('\nStarting File-Connectivity Analysis...', end = '')
        flawedFilesOutput = 'text_data\otero-'+folderName+'-flawedFiles.txt' 
        connect_flawedFiles(auth2flawedFiles, flawedFilesOutput) # auth2files input -> file2file output
        columnTypes = ['document', 'document'] # left column type, right column type
        response = input("Generate File-File Lynsoft XLSX for "+folderName+"? [y]/n\n")
        XLSXoutput = 'xl_data\lynks\oterolynks-'+folderName+'-flawedFiles.xlsx'
        if(response == "y"):
            makelynks.genXLSX(flawedFilesOutput, columnTypes, XLSXoutput)

            
        # TODO implement option to delete leftover text files
        response = input('Delete .txt files? [y]/n\n')        
        if(response == "y"):
            print("Delete all files that start with 'otero-' and end with '.txt'")
    
    else:
        print('Please analyze '+folderName+' in SonarQube and export the results before continuing.')


    
    
    
    
    
    
    
    