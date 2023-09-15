# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 20:40:35 2023

@author: camartinezm
"""

import sys
from pathlib import Path

# Add working directory in PATH
project_dir = Path(__file__).resolve().parents[2]
file_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(file_dir))

DATA_PATH = file_dir / "data"  # Directory for data