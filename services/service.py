# -*- coding: utf-8 -*-
#
# Copyright © 2023 CamiloMartinezM
# Licensed under the terms of the MIT License
#
# File: services/myservice.py
# Description: This file defines the DataRetrievalService class, which handles the main 
# functionality of file data retrieval of the tool.
from . import config as cf
import json

assert cf

import os

class DataRetrievalService:
    def get_origin_file_path(self, file_name: str) -> str:
        # Replace this with your actual functionality
        self.file_path = cf.DATA_PATH / file_name
        return cf.DATA_PATH / file_name
    
    def get_origin_file_type(self) -> str:
        return self.file_path.suffix[1:]

class DataExportService:
    def export_json_to_data_path(self, json_dict: dict, output_file_name: str) -> None:
        with open(cf.DATA_PATH / output_file_name, "w") as outfile:
            json.dump(json_dict, outfile, indent=4, sort_keys=False)
            
    def generate_png_from_json(self, json_file_name: str) -> None:
        os.system("erdot " + str(cf.DATA_PATH / json_file_name))
        os.system("dot " + str(cf.DATA_PATH / "parsed.dot") + " -Tpng -o " + str(cf.DATA_PATH / "generated.png"))
        
    def string_to_er_file(self, raw_string: str) -> None:
        with open(cf.DATA_PATH / "parsed.er", "w") as f:
            f.writelines(raw_string)
    
    def generate_from_er(self, er_file_name: str, output_file_name: str, output_format: str) -> None:
        if output_format == "pdf":
            os.system(f"docker run -i erd:0.2.1.0 < {str(cf.DATA_PATH / er_file_name)} > {str(cf.DATA_PATH / output_file_name)}.{output_format}")