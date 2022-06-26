import os
import winsound
import Modelado
from Escenarios.Scripts import EscenarioAleatorio


directory_path = "./"

EscenarioAleatorio.escenarioAleatorio(1,2,1,0.05,0.5,"../../")

directory = os.fsencode(directory_path)
for file in os.listdir(directory):

    filename = os.fsdecode(file)
    if filename.endswith("ario.json"):
        print(filename)
        file_path = os.path.join(directory_path, filename)
        execResults = Modelado.ejecutarModeloPyomo(file_path)


        execResults["Modelo"] = "Pyomo"
        execResults["Escenario"] = filename[:-5]



        resultsLine = str(execResults["Modelo"]) + "," + str(execResults["Escenario"]) + "," + \
                      str(execResults["FO_Global"]) + str(execResults["Tiempo"])

        while True:
            duration = 1000  # milliseconds
            freq = 440  # Hz
            winsound.Beep(freq, duration)
