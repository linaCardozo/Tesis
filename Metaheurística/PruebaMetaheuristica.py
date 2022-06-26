import numpy as np
from HeuristicaMultiprocessing import heuristica

def pruebaMetaheuristica(n, iteraciones, hormigas, ordenes):
    
    resTiempo = []
    resObj = []
    # fileName = "Pruebas/PC Base/Escalabilidad/Dask/Ordenes" + str(ordenes) + ".txt"
    fileName = "Pruebas/PC 8GB/TempMP/Metaheuristica" + str(n) + "N" + str(iteraciones) + "I" + str(hormigas) + "H.txt"
    
    with open(fileName, 'w') as f:
        f.write("Tiempos de ejecución y valor de la función objetivo de metaheurística con " + str(n) 
                + " repeticiones de " + str(iteraciones) + " iteraciones y " + str(hormigas) + " hormigas:\n")    
        f.write("\n(Tiempo de ejecución, Valor función objetivo)\n")
        
        for i in range(n):
            res = heuristica(iteraciones, hormigas, ordenes)
            resTiempo.append(res[0])
            resObj.append(res[1])
            f.write(str(res) + "\n")
            
        f.write("\nPromedio de tiempos:\n")
        f.write(str(np.mean(resTiempo)) + " segundos\n")
        f.write(str(np.mean(resTiempo)*1000) + " milisegundos\n")
        f.write("\nDesviación estándar:\n")
        f.write(str(np.std(resTiempo)) + " segundos\n")
        f.write(str(np.std(resTiempo)*1000) + " milisegundos\n")
        f.write("\nPromedio valor función objetivo:\n")
        f.write(str(np.mean(resObj)))
        f.write("\nDesviación estándar valor función objetivo:\n")
        f.write(str(np.std(resObj)))
        
        print("Ejecución exitosa")
        
    f.close()
    
# for i in range(170, 240, 10):
#     pruebaMetaheuristica(5, 40, 40, i)

for i in range(10, 70, 10):
    for j in range(10, 100, 10):
        pruebaMetaheuristica(50, i, j, 14)