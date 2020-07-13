# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 20:57:54 2019

@author: damon
"""
import os
from git import Repo

# downloads the github 'che' repo
def download(gitURL):
    response = input('Do you want to download '+gitURL+'?\n[y]/n\n')
    if(response == 'y'):
        print('Attempting download of git repo \'' + gitURL + '\'')    
        folderName = gitURL.rsplit('/', 1)[-1] # last part of gitURL
        
        folPath = os.getcwd() + '\\'+folderName
        
        try: # download repo to machine
            os.mkdir(folPath) # create new folder from current working direc
            print("Directory "+ folPath+" created.") 
            print("Downloading "+folderName+" repository to current working "+
                  "directory (this may take a while).")
            Repo.clone_from(gitURL, folPath) # download github repo to chePath
            print("Download complete.\n")
        except FileExistsError: # folder already exists
            print("Directory " + folPath+  " already exists.\n"+
                  "If you wish to download a new version of the repo, "+
                  "please delete the '" +folderName+ "' folder and retry.")