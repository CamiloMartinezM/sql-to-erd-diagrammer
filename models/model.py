# -*- coding: utf-8 -*-
#
# Copyright © 2023 CamiloMartinezM
# Licensed under the terms of the MIT License
#
# File: models/mymodel.py
# Description: This file defines the EntityModel class, which represents the data
# that the tool is working with.

import pandas as pd
import itertools
import json
import os


class EntityModel:
    def __init__(self) -> None:
        self.tables = {}
        self.tables_metadata = {}
        self.tables_relationships = []
        self.columns_relationships = []

    def define_tables_from_file(
        self, file_type: str, data_file: str, sheet_name: str
    ) -> None:
        self.raw_data = self.read_raw_data(file_type, data_file, sheet_name)

        for _, row in self.raw_data.iterrows():
            table_name = row["Table"]
            column_name = row["Column name"]
            column_type = row["Type"]

            if column_type == "datetime":
                data_type = "datetime"
            elif column_type == "varchar":
                data_type = f'varchar({int(row["Length"])})'
            elif column_type == "numeric":
                data_type = f'numeric({int(row["Precision"])}, {int(row["Scale"])})'
            else:
                data_type = "unknown"

            if table_name not in self.tables:
                self.tables[table_name] = {}
            
            if table_name not in self.tables_metadata:
                self.tables_metadata[table_name] = {}
                self.tables_metadata[table_name]["Module"] = row["Module"]

            self.tables[table_name][column_name] = data_type
            if (
                pd.notna(row["FK column"])
                and pd.notna(row["FK Table"])
                and row["Key"] == "FK"
            ):
                self.tables_relationships.append(
                    (row["Table"], "*--*", row["FK Table"])
                )
                self.columns_relationships.append(
                    (
                        (row["Table"], row["Column name"]),
                        "*--*",
                        (row["FK Table"], row["FK column"]),
                    )
                )

    def read_raw_data(
        self, file_type: str, data_file: str, sheet_name: str = ""
    ) -> pd.DataFrame:
        if file_type == "csv":
            return pd.read_csv(data_file, sep=",")
        elif file_type == "xlsx":
            if sheet_name != "":
                return pd.read_excel(data_file, sheet_name=sheet_name)
            else:
                return pd.read_excel(data_file)
        else:
            return None

    def extract_table(
        self,
        table: str,
        exclude: set = {},
        exclude_per_table: dict = None,
    ) -> dict:
        filtered = self.tables[self.tables.TABLE_NAME == table][
            ["COLUMN_NAME", "DATA_TYPE"]
        ]
        cols = filtered.set_index("COLUMN_NAME").to_dict()["DATA_TYPE"]

        for excluded_col in exclude | EntityModel.pop_default(
            exclude_per_table, table, set()
        ):
            if excluded_col in cols:
                cols.pop(excluded_col)

        return {table: cols}

    def extract_tables(self, table_names: list, exclude_per_table: dict = None) -> dict:
        tables = {}
        for table in table_names:
            tables = {
                **tables,
                **self.extract_table(table, exclude_per_table=exclude_per_table),
            }

        return tables

    def movetoend(self, table: str, key: str) -> None:
        self.tables[table][key] = self.tables[table].pop(key)

    def movetostart(self, table: str, key: str) -> None:
        self.tables[table] = {key: self.tables[table].pop(key), **self.tables[table]}

    def movekey(self, table: str, key: str, steps: int) -> None:
        keys = list(self.tables[table].keys())
        current = keys.index(key)
        del keys[current]
        wanted = (current + steps) % len(keys)
        new_table = {}
        i = 0
        while i < len(keys):
            curr_key = keys[i]
            if i == wanted:
                new_table = {**new_table, key: self.tables[table][key]}

            new_table = {**new_table, curr_key: self.tables[table][curr_key]}
            i += 1

        self.tables[table] = new_table

    def get_tables(self, mode: str = "default", filter_params: list = []) -> dict:
        if mode == "default" and not filter_params:
            return self.tables
        elif mode == "default" and filter_params:
            return self.filter_tables(filter_params)
        else:
            return None
    
    def filter_tables(self, filter_params: list = []) -> dict:
        """Filters the entity model tables with a list of filters.

        Parameters
        ----------
        filter_params : list, optional
            It should be a list of dictionaries. For example,
                
                filter_params = [{"metadata": {"Module": ["Rates Management"]}}]
            
            Which means that the tables will be filtered by their metadata,
            particularly the "Module" key in their metadata which has to be
            equal to "Rates Management". The default is [].

        Returns
        -------
        dict
            Filtered self.tables.
        """
        filtered_tables = self.tables.copy()
        for filter_param in filter_params:
            for filter_scope, scope_values in filter_param.items():
                if filter_scope == "metadata":
                    for metadata_key, wanted_values in scope_values.items():
                        temp = filtered_tables.copy()
                        for table in filtered_tables:
                            if self.tables_metadata[table][metadata_key] not in wanted_values:
                                temp.pop(table)
                        filtered_tables = temp
        return filtered_tables
    
    def filter_columns_relationships(self, by_tables: list = []) -> dict:
        filtered_cols_relationships = []
        for rel in self.columns_relationships:
            table_column, cardinality, fktable_column = rel
            table, _ = table_column
            fktable, _= fktable_column
            if table in by_tables and fktable in by_tables:
                filtered_cols_relationships.append(rel)
        
        return filtered_cols_relationships

    def get_columns_relationships(self, mode: str = "default", filter_tables: list = []) -> dict:
        cols_relationships = self.columns_relationships.copy()
        if filter_tables: 
            cols_relationships = self.filter_columns_relationships(filter_tables)
            
        if mode == "list[str]":
            list_str = []
            for relationship in cols_relationships:
                list_str.append(
                    f"{relationship[0][0]}:{relationship[0][1]} {relationship[1]} {relationship[2][0]}:{relationship[2][1]}"
                )
            return list_str
        elif mode == "default":
            return cols_relationships
        
    def get_tables_relationships(self, mode: str = "default", filter_tables: list = []) -> dict:
        tabs_relationships = self.tables_relationships.copy()
        if filter_tables: 
            tabs_relationships = self.filter_tables_relationships(filter_tables)
            
        if mode == "list[str]":
            list_str = []
            for relationship in tabs_relationships:
                list_str.append(
                    f"{relationship[0]} {relationship[1]} {relationship[2]}"
                )
            return list_str
        elif mode == "default":
            return tabs_relationships
        
    def filter_tables_relationships(self, by_tables: list = []) -> dict:
        filtered_tables_relationships = []
        for rel in self.tables_relationships:
            table, cardinality, fktable = rel
            if table in by_tables and fktable in by_tables:
                filtered_tables_relationships.append(rel)
        
        return filtered_tables_relationships
        

    def return_raw_data(self) -> pd.DataFrame:
        return self.raw_data

    @classmethod
    def pop_default(input_, index, default_value):
        try:
            return input_[index]
        except KeyError:
            return default_value
