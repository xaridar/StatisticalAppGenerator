#!/bin/bash

pip install -r requirements.txt
if command -v Rscript &> /dev/null
then
    Rscript install.packages("shinylight", repos = "https://cloud.r-project.org")
fi
main.py