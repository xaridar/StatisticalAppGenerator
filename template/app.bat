@echo off
python -m pip install -r requirements.txt --user
where /q Rscript
IF ERRORLEVEL 1 (
    ECHO No R installation; skipping.
) ELSE (
    Rscript install.packages("shinylight", repos = "https://cloud.r-project.org")
)
python main.py