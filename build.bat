@echo off

python -m PyInstaller generate_app.py --add-data ./template:./template --add-data schema.json:. --add-data icon.png:. --collect-data grapheme --collect-data sv_ttk -F --clean --icon=icon.ico --name sag