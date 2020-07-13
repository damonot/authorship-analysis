# Checks if an output folder for the repo has already been generated. Generates one if not.
import os

def check(verbose, repo):
  if verbose:
    print("Checking if {} exists in 'output' folder...".format(repo)) 
  path = os.getcwd() + "\\output\\" + repo
  
  if not os.path.exists(path):
    os.makedirs(path)
    if verbose:
      print("\t{} created in 'output' folder.".format(repo))
  else:
    if verbose:
      print("\t{} already exists in 'output' folder.".format(repo))
  