CALL bicon-venv\Scripts\activate.bat
CALL pip install -r requirements_bicon-venv.txt
CALL echo bicon-venv activated
CALL python bicluster.py %1 %2 %3