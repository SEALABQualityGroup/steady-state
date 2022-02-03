#!/bin/bash

python create_dyredata.py
bash dynamic_reconfiguration.sh
python create_dynconfig.py