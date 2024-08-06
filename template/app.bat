@echo off
pip install -r requirements.txt
where /q Rscript
IF ERRORLEVEL 1 (
    ECHO No R insttallation; skipping.
) ELSE (
    Rscript install.packages("shinylight", repos = "https://cloud.r-project.org")
)
main.py