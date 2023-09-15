# -*- coding: utf-8 -*-
#
# Copyright © 2023 CamiloMartinezM
# Licensed under the terms of the MIT License
#
# File: controllers/mycontroller.py
# Description: This file defines the MyController class, which controls the 
# flow of the application.
from services.service import DataRetrievalService, DataExportService
from models.model import EntityModel

class MyController:
    def __init__(self, view):
        self.view = view
        self.in_service = DataRetrievalService()
        self.out_service = DataExportService()

    def run_from_file(self, file_name: str, sheet_name: str = "") -> None:
        data = self.in_service.get_origin_file_path(file_name)
        self.model = EntityModel()
        self.model.define_tables_from_file(
            self.in_service.get_origin_file_type(), 
            data, 
            sheet_name
        )
        
    def entity_model_to_json(self, output_file_name: str, filter_params: list = []) -> None:
        tables = self.model.get_tables(filter_params=filter_params)
        json_dict = {
            "tables": tables,
            "relations": self.model.get_columns_relationships(mode="list[str]", filter_tables=list(tables.keys())),
            "rankAdjustments": "",
            "label": "",
        }
        
        self.out_service.export_json_to_data_path(json_dict, output_file_name)
        
    def entity_model_to_er_format(self, output_file_name: str, filter_params: list = []) -> None:
        tables = self.model.get_tables(filter_params=filter_params)
        tables_relationships = self.model.get_tables_relationships(mode="list[str]", filter_tables=list(tables.keys()))
        
        er_string = "# Entities\n"
        for table in tables:
            er_string += f"[{table}] "
            
            """if table in bgcolors:
                f.write('{bgcolor: "' + bgcolors[table] + '"}')
            """
            er_string += "\n"
            
            for col, label in tables[table].items():
                er_string += f"\t{col} " + '{label: "' + label + '"}\n'

            er_string += "\n"

        er_string += "# Relationships\n"
        for relationship in tables_relationships:
            er_string += "\t" + relationship + "\n"
                
        dot_position = output_file_name.rfind(".")        
        if dot_position != -1:
            # Extracting the substring from the last occurrence of "." till the end
            format_extension = output_file_name[dot_position + 1:]
                
        self.out_service.string_to_er_file(er_string)
        self.out_service.generate_from_er("parsed.er", output_file_name[:dot_position], format_extension)
        
    def generate_png(self, json: str) -> None:
        self.out_service.generate_png_from_json(json)
        
    def return_model(self):
        return self.model