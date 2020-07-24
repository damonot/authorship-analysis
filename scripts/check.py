# Checks if an output folder for the repo has already been generated. Generates one if not.
import os

def folder(verbose, folder):
  #if verbose:
  #  print("Checking if {} exists in 'output' folder...".format(repo)) 
  path = os.getcwd() + "\\output\\" + folder
  
  if not os.path.exists(path):
    os.makedirs(path)
    if verbose:
      print("\t{} created in 'output' folder.".format(folder))
  else:
    if verbose:
      print("\t{} folder already exists in 'output'".format(folder))

def fyle(verbose, repo, fyle):
  if os.path.isfile(fyle):
    return True
  else:
    return False