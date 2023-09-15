# -*- coding: utf-8 -*-
#
# Copyright © 2023 CamiloMartinezM
# Licensed under the terms of the MIT License
#
# File: main.py
# Description: This is the main entry point of the application. It creates 
# instances of the view and controller, and starts the application.

from controllers.controller import MyController
from views.view import ConsoleView

ORIGIN_FILE_NAME = 'Entity Model Dictionary_v2.xlsx'
SHEET_NAME = 'DEF'

'''def main():
    view = ConsoleView()
    controller = MyController(view)
    controller.run_from_file(ORIGIN_FILE_NAME, SHEET_NAME)
    
    
if __name__ == '__main__':
    main()
'''
view = ConsoleView()
controller = MyController(view)
controller.run_from_file(ORIGIN_FILE_NAME, SHEET_NAME)
# controller.entity_model_to_json("parsed.json", filter_params=[{"metadata": {"Module": ["Taxes Management"]}}])
controller.entity_model_to_er_format("generated.pdf", filter_params=[{"metadata": {"Module": ["Enterprise Structure"]}}])
model = controller.return_model()

controller.generate_png("parsed.json")
