CALL bicon-venv\Scripts\activate.bat
CALL pip install bicon
CALL pip install openpyxl
CALL echo bicon-venv activated
CALL python bicluster.py %1 %2 %3