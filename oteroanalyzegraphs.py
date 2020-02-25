# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 18:55:22 2020

@author: damon
"""
import os
import math
import pandas as pd
import xlsxwriter
from openpyxl import load_workbook

def runner(repo):
    cwd = os.getcwd()
    auth2flawsXL = cwd + '\\oterolynks-'+repo+'-auth2flaws.xlsx'
    auth2filesXL = cwd + '\\oterolynks-'+repo+'-auth2flawedFiles.xlsx'
    coworkersXL = cwd + '\\oterolynks-'+repo+'-coworkers.xlsx'
    
    excelList = [auth2flawsXL, auth2filesXL, coworkersXL]
    
    response = input('Degree Centrality? [y]/n\n')
    if(response == 'y'):
        for xl in excelList:    
            #gen_degreeCentrality(xl, repo)
            print('\n')


    bugvulnfile = 'otero-'+repo+'-auth2flawedFiles.txt' # raw complete file
    folder = os.getcwd() + '\\text_data\\'
    path = folder + bugvulnfile
    #print(path)
    
    # bf*iaf bug uniqueness distribution for each author
    #response = input('Bug-Frequency * Inverse Author Frequency? [y]/n\n')
    #if(response == 'y'):
    bf_iaf(path, repo)
    
        
#bug-frequency2inverseauthorfrequency
def bf_iaf(txt, repo):

    bugs = []
    authors = []
    bugLines = []
    with open(txt, encoding='utf-8') as t:
        for line in t:
            fields = line.split(' \t ') # 0auth | 1file | 2flawtype | 3line | 4info |
            if(fields[2] == 'bug'): # is a bug?
                bugLines.append(fields) # copy necessary lines into list
                bug = fields[4]
                auth = fields[0]
                if(bug not in bugs): # bug not encountered yet
                    bugs.append(bug)
                    #print(bug)
                if(auth not in authors): # author not encountered yet
                    authors.append(auth)
    
    nAuth = len(authors) # number of authors
    
    #BF calculation
    listDict = [] # list of freqDict
    for auth in authors:
        freqDict = {} # of times each bug is connected to auth
        #print("Calculating Bug Distribution for Author: " +auth)
        for line in bugLines:
            if(line[0] == auth):
                bug = line[4]
                if(bug not in freqDict):
                    freqDict[bug] = 1
                else:
                    freqDict[bug] +=1
        
        listDict.append([auth, freqDict]) # author & their bug freq dist
    
    '''structure is...
    list: tups
        tup: author, dict
            dict: bug, freq '''
    #AF calculation: num authors who have written a particular bug
    
    encounteredBugs = []
    authsPerBug = {} # bug | num auths who have written it
    for tup in listDict:
        auth = tup[0]
        for bug in tup[1]: # iterate through bugs of auths freqdist dict
            if bug not in encounteredBugs: # new author of bug
                authsPerBug[bug] = 1
                encounteredBugs.append(bug)
            else: authsPerBug[bug] += 1 # additional author of existing bug
    
    
    '''structure is...
    list: tups
        tup: author, dict
            dict: bug, bfiaf '''
    #BF IAF calculation
    bfiafs = []
    for auth in authors:
        bfiafs.append((auth, {}))
    
    authbfiaf = {}
    for bug in authsPerBug:
        iafeqn = (1 + nAuth)/(1+authsPerBug[bug])
        iaf = math.log(iafeqn,2)
        for tup in listDict: # (auth, {bug, count})
            auth = tup[0]
            authIndex = listDict.index(tup)
            if(bug in tup[1]):
                bugfreq4auth = tup[1][bug] # [1] selects dict, [bug] selects key
            else: bugfreq4auth = 0
            bfiafval = bugfreq4auth * iaf
            
            # append bug and bfiafval to dict
            bfiafs[authIndex][1].update( {bug : bfiafval} ) 
    
    return bfiafs
    

def gen_degreeCentrality(xlLoc, repo):
    print(xlLoc)
    xls = pd.ExcelFile(xlLoc)
    df1 = pd.read_excel(xls, 'relations')
    
    
    auths = {}
    for row in df1['node1']:
        if row not in auths:
            auths[row] = 1
        else:
            auths[row] +=1


    sheetName = xlLoc[xlLoc.rindex('-')+1:] # save text after last dash
    xlName = repo+'-degreecentrality.xlsx'
    df2 = pd.DataFrame(list(auths.items()),columns = ['node','count'])
    df2 = df2.sort_values('count', ascending=False) # sort in descending order
    print('output xl: '+xlName)
    df2excel(df2, xlName, sheetName) # convert dataframe to excel doc


# convert dataframe to excel
def df2excel(df, xlName, sheetName):
    
    if not(os.path.isfile(xlName)):
        print(xlName+' DNE')
        writer = pd.ExcelWriter(xlName, engine='xlsxwriter')
        writer.save()
    else: print() # do nothing #print(xlName+ ' already exists')
        
    with pd.ExcelWriter(xlName, engine='openpyxl') as writer:
        writer.book = load_workbook(xlName)
        df.to_excel(writer, sheetName, index=False)
    


    
#oterolynks-phpmyadmin-auth2flaws.xlsx


