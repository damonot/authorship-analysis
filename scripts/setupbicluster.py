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
  if verbose:
    print(path)
  if os.path.exists(path):
    return True
  else:
    return False

def setup_venv(verbose, overwrite, repo):
  if verbose:    
    print("No 'bicon-venv' folder found. Setting up Bi-Cluster (BiCon) Virtual Environment...")
  os.system('cmd /k "python -m venv bicon-venv"')

def start_venv(verbose, overwrite, repo):
  if verbose:
    print("launching bicon-venv...")

  batch = os.getcwd() + '\scripts\startbiconvenv.bat'
  #os.system('cmd /k "'+batch+'"')

  os.system('cmd /k "start cmd.exe /k "'+batch+'"')

  #subprocess.run([batch])

  #subprocess.call([r'C:\Users\Ron\Desktop\Run Batch\Matrix.bat'])