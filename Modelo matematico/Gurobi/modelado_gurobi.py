# Modelado - Proyecto de Grado

from gurobipy import *
import numpy as np
import time
import json
from Pruebas.Grafos import CrearMapa


def ejecutarModeloGurobi(filePath,iteracion):

    ### Ejecución del modelo
    timerGeneralInicial = time.time()

    ### Parámetros de generación de datos

    stageFile = open(filePath, )
    stageData = json.load(stageFile)

    numEmpleados = stageData["numEmpleados"]
    numOrdenes = stageData["numOrdenes"]
    numDiasOperacion = stageData["numDiasOperacion"]
    numHabilidades = stageData["numHabilidades"]

    ### Conjuntos

    E = range(0, numEmpleados)  # Conjunto de Empleados
    O = range(0, numOrdenes + 1)  # Conjunto de Ordenes
    D = range(0, numDiasOperacion)  # Conjunto de Dias de operación
    S = range(0, numHabilidades)  # Conjunto de Habilidades

    ### Parámetros

    # Parámetro de disponibilidad horaria por empleado
    tiemD = {(o, a): np.asarray(stageData["tiempoDesplazamiento"])[i][j] for o, i in enumerate(O)
             for a, j in enumerate(O)}

    # Parámetro de disponibilidad horaria por orden
    tiemA = {(o): np.asarray(stageData["tiempoAtencion"])[i] for o, i in enumerate(O)}

    # Parámetro de costos de ANS
    costosANS = {(o): np.asarray(stageData["costosANS"])[i] for o, i in enumerate(O)}

    # Parámetro de maxDia de cada órden
    maxDia = {o: np.asarray(stageData["maxDia"])[i] for o, i in enumerate(O)}

    # Parámetro de prioridad por orden
    prioridad = {o: np.asarray(stageData["prioridad"])[i] for o, i in enumerate(O)}

    # Parámetro de las habilidades de cada empleado
    habilidadesOperarios = {(e, s): np.asarray(stageData["habilidadesOperarios"])[i][j] for e, i in enumerate(E)
                            for s, j in enumerate(S)}

    # Parámetro de las habilidades requeridas en cada orden
    habilidadesOrdenes = {(o, s): np.asarray(stageData["habilidadesOrdenes"])[i][j] for o, i in enumerate(O)
                          for s, j in enumerate(S)}

    # Parámetro de porcentaje de cumplimiento de requerimiento en habilidades en cada orden
    porcentajeCumplimientoHabilidades = stageData["porcentajeCumplimientoHabilidades"]

    horasT = {(e, d): np.asarray(stageData["horasTrabajo"])[i][j] for e, i in enumerate(E)
              for d, j in enumerate(D)}

    stageFile.close()

    ### Modelo

    model = Model("asignacion")

    ### Variables de decisión

    x = model.addVars(len(E), len(O), len(D), len(O), vtype=GRB.BINARY, name='x')
    aux = model.addVars(len(E), len(D), vtype=GRB.BINARY, name='aux')
    u = model.addVars(len(E), len(O), len(D), vtype=GRB.INTEGER, name='u')
    minx = model.addVars(len(D), vtype=GRB.INTEGER, name='minx')
    ans = model.addVars(len(O), vtype=GRB.INTEGER, name='ans')
    auxMaxDia = model.addVars(len(O), vtype=GRB.BINARY, name='auxMaxDia')
    ### Restricciones

    # Una orden solo puede tener un empleado asignado, solo puede ser atendida en un día y solo debe tener un antecesor
    for o in O:
        if o != 0:
            model.addConstr(quicksum(x[e, o, d, a] for e in E
                                     for a in O
                                     for d in D) <= 1)  # Debería ser <= 1

    # Un empleado solo puede trabajar Ht horas al día
    for e in E:
        for d in D:
            model.addConstr(quicksum(x[e, o, d, a] * (tiemD[o, a] + tiemA[o]) for o in O
                                     for a in O) <= horasT[e, d])

    # El antecesor debe ser diferente de la orden
    model.addConstr(quicksum(x[e, o, d, o] for e in E
                             for o in O
                             for d in D) <= 0)

    # Los empleados deben partir de la orden 0

    for e in E:
        for d in D:
            for a in O:
                if a == 0:
                    model.addConstr(quicksum(x[e, o, d, a] for o in O) - aux[e, d] == 0)

    # Los empleados deben llegar al punto 0 (la empresa)
    for e in E:
        for d in D:
            for a in O:
                if a == 0:
                    model.addConstr(quicksum(x[e, a, d, o] for o in O) - aux[e, d] == 0)

    # Ordenes intermedias
    for e in E:
        for d in D:
            for a in O:
                if a != 0:
                    model.addConstr(quicksum(x[e, o, d, a] for o in O) - quicksum(x[e, a, d, o] for o in O) == 0)
    # Evitar Subciclos
    for e in E:
        for d in D:
            for o in O:
                if o != 0:
                    model.addConstr(u[e, o, d] <= 999 * quicksum(x[e, o, d, a] for a in O))

    for e in E:
        for d in D:
            for o in O:
                if o != 0:
                    model.addConstr(u[e, o, d] >= quicksum(x[e, o, d, a] for a in O))

    for e in E:
        for d in D:
            for o in O:
                for a in O:
                    if o != 0 and a != 0:
                        model.addConstr((u[e, o, d] - u[e, a, d]) <= 999 * (1 - x[e, o, d, a]) - 1 + 999 * (
                                    1 - quicksum(x[e, a, d, i] for i in O)))

    for e in E:
        for d in D:
            for o in O:
                if o == 0:
                    model.addConstr(u[e, o, d] == 0)

    for e in E:
        for d in D:
            for o in O:
                model.addConstr(u[e, o, d] <= quicksum(x[e, i, d, a] for i in O
                                                       for a in O))

    # Acotar variable auxiliar

    for e in E:
        for d in D:
            model.addConstr(999 * aux[e, d] >= quicksum(x[e, o, d, a] for o in O
                                                        for a in O))

    for e in E:
        for d in D:
            model.addConstr(aux[e, d] <= quicksum(x[e, o, d, a] for o in O
                                                  for a in O))

    for e in E:
        for d in D:
            model.addConstr(minx[d] <= quicksum(x[e, o, d, a] for o in O
                                                for a in O))

    # El empleado debe cumplir con unas habilidades minimas
    for o in O:
        for d in D:
            for a in O:
                for e in E:
                    model.addConstr(quicksum(
                        x[e, o, d, a] * habilidadesOrdenes[o, s] * habilidadesOperarios[e, s] for s in
                            S) >= porcentajeCumplimientoHabilidades * quicksum(
                            x[e, o, d, a] * habilidadesOrdenes[o, s] for s in S))

    # Acota dias que se tarda una orden en ser atendida desde su dia maximo
    for o in O:
        model.addConstr((quicksum(x[e, o, d, a] * d for e in E
                                  for a in O for d in D)) - maxDia[o] <= ans[o] + 9999 * (1 - auxMaxDia[o]))
    for o in O:
        model.addConstr((quicksum(x[e, o, d, a] * d for e in E
                                  for a in O for d in D) - maxDia[o]) <= 9999 * (auxMaxDia[o]))

    for o in O:
        ans[o] >= 0

    # Función Objetivo - Cumplimiento de órdenes
    FO_Cumplimiento = quicksum(x[e, o, d, a] * prioridad[o] for e in E
                               for o in O
                               for d in D
                               for a in O)

    FO_Tiempo = quicksum(x[e, o, d, a] * (1/(tiemD[a,o]+1)) for e in E
                               for o in O
                               for d in D
                               for a in O)



    # Función Objetivo - Costo por incumplimiento de ANS
    FO_ANS = quicksum(costosANS[o] * ans[o] * prioridad[o] for o in O)

    FO_Minmax = quicksum(minx[d] for d in D)

    model.setObjective(FO_Cumplimiento +
                       FO_Minmax * 0.05 - FO_ANS + FO_Tiempo)

    ##



    model.ModelSense = GRB.MAXIMIZE
    model.setParam('NonConvex', 2)
    model.setParam('OutputFlag', 0)
    model.optimize()

    timerGeneralFinal = time.time()
    timerGeneral = timerGeneralFinal - timerGeneralInicial

    ### Consulta de resultados
    for e in E:
        for d in D:
            for o in O:
                for a in O:
                    print(x[e, o, d, a])
    
    print("\n")
    print("Función Objetivo total: " + str(FO_Cumplimiento.getValue() +
                                           FO_Minmax.getValue() * 0.05 - FO_ANS.getValue() - (numEmpleados * numDiasOperacion)))
    print("Función Objetivo 0 (Ordenes asignadas): " + str(FO_Cumplimiento.getValue() - (numEmpleados * numDiasOperacion)))
    print("Función Objetivo 1 (Minmax): " + str(FO_Minmax.getValue()))
    print("\n")
    print("aux dias es " + str(auxMaxDia[o]))

    for d in D:
        print("Dia ac " + str(d) + " Min ordenes " + str(minx[d]))




    print("\n")
    print("Tiempo de ejecución total: " + str(round(timerGeneral, 2)) + " segundos")

    ordenes=[]
    for d in D:

        for e in E:
            for a in O:
                for o in O:
                    if x[e, o, d, a].X == 1:
                        ordenes.append(a)
                        ordenes.append(o)
                        #print("parte de " + str(a) + " hasta " + str(o))
    
    CrearMapa.crearMapa(ordenes, iteracion,"Exacto")

    ### Consulta de resultados
    for e in E:
        for d in D:
            for o in O:
                print("aux dias es " + str(auxMaxDia[o]))
                print("ans es " + str(ans[o]))
    
    print("\n")
    print("Función Objetivo total: " + str(FO_Cumplimiento.getValue() +
                                           FO_Minmax.getValue() * 0.05 - FO_ANS.getValue() - (
                                                       numEmpleados * numDiasOperacion)))
    print("Tiempo de ejecución total: " + str(round(timerGeneral, 2)) + " segundos")

    ordenes = quicksum(x[e, o, d, a] for e in E for o in O for d in D for a in O)

    results = {"FO_Global": (FO_Cumplimiento.getValue() +
                             FO_Minmax.getValue()),
               "FO_Ordenes": FO_Cumplimiento.getValue(),
               "FO_Distancia": FO_Minmax.getValue(),
               "Tiempo": timerGeneral}
    return results