import os
import subprocess

def go(verbose, overwrite, repo):
  
  setup = check_setup(verbose, overwrite)

  if not setup:
    setup_venv(verbose, overwrite, repo)
  else:
    if verbose:
      print("bicon-venv already setup.")

  start_venv(verbose, overwrite, repo)

def check_setup(verbose, overwrite):
  path = os.getcwd() + "\\bicon-venv"
  if os.path.exists(path):
    return True
  else:
    return False

def setup_venv(verbose, overwrite, repo):
  if verbose:    
    print("No 'bicon-venv' folder found. Setting up Bi-Cluster (BiCon) Virtual Environment...")
  os.system('cmd /c "python -m venv bicon-venv"')
  

def start_venv(verbose, overwrite, repo):
  if verbose:
    print("launching bicon-venv for {}...".format(repo))

  batch = os.getcwd() + '\scripts\startbiconvenv.bat'
  os.system('cmd /c "start cmd.exe /k "{} {} {} {}"'.format(batch, verbose, overwrite, repo)) # TODO change /k to /c when done implementing