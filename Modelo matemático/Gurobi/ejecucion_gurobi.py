# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 11:56:40 2020

@author: Daniel
"""

import modelado_gurobi
from Escenarios.Scripts import EscenarioAleatorio
#import modelado_gurobi_copia
import os



directory_path = "./" 

#CrearEscenario.crearEscenario(2,16,1,0.05)
def ejecucion_gurobi(i):

    directory = os.fsencode(directory_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith("ario.json"):
            print (filename)
            file_path = os.path.join(directory_path, filename)

            execResults = modelado_gurobi.ejecutarModeloGurobi(file_path,i)
            execResults["Modelo"] = "Gurobi"
            execResults["Escenario"] = filename[:-5]

            resultsLine = str(execResults["Modelo"]) + "," + str(execResults["Escenario"]) + "," + \
                          str(execResults["FO_Global"]) + str(execResults["Tiempo"])

ejecucion_gurobi(500)