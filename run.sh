#!/bin/bash

if [[ ! -d "psychom" ]];
then
    python3 -m venv psychom
fi

source psychom/bin/activate
pip install -r requirements.txt
python3 psycho_mnt.py
