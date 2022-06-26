import random
import json
import copy
import time
import os

import numpy

import CrearEscenario
import EscenarioAleatorio
import CrearMapa

import multiprocessing as mp

def darProbabilidad(matriz, tiempo, nodoActual, feromonas, alpha, beta, habOrdenes, habEmpleados, q):

    probabilidad = []
    vector = []

    for i in range(len(matriz)):
        if (matriz[nodoActual][i] != 0):

            #Una orden solo puede ser antendida por un empleado con un minimo de habilidades
            if(sum(numpy.array(habOrdenes[i]) * numpy.array(habEmpleados)) >= q * sum(numpy.array(habOrdenes[i]))):
                vector.append(round(beta / matriz[nodoActual][i] + alpha * feromonas[nodoActual][i], 2))
            else:
                vector.append(0)
        else:
            vector.append(0)

    vector[0] = 0

    suma = sum(vector)
    if(suma == 0):
        return probabilidad

    #Calcular probabilidades
    for i in range(len(matriz)):
        if matriz[nodoActual][i] == 0:
            if len(probabilidad) > 0:
                probabilidad.append(probabilidad[i - 1])
            else:
                probabilidad.append(0)
        else:
            if (matriz[nodoActual][i] + matriz[i][0]) < tiempo:
                if len(probabilidad) > 0:
                    probabilidad.append(vector[i] / suma + probabilidad[i - 1])
                else:
                    probabilidad.append(vector[i] / suma)
            else:
                if len(probabilidad) > 0:

                    probabilidad.append(probabilidad[i - 1])
                else:
                    probabilidad.append(0)
    return probabilidad


def borrarNodo(nodoActual, matriz):
    for i in range(len(matriz)):
        matriz[i][nodoActual] = 0
    return matriz


def actualizarFeromonas(secuencia, valorsecuencias, feromonas, rho):
    deltaFeromonas = []

    #Inicializar delta feromonas
    for i in range(len(feromonas)):
        deltaFeromonas.append(numpy.repeat(0, len(feromonas)).tolist())

    #Calcular delta feromonas
    for i in range(len(secuencia)):
        for j in range(len(secuencia[i]) - 1):
            deltaFeromonas[secuencia[i][j]][secuencia[i][j + 1]] += valorsecuencias[i]

    #Retorna feromonas con evaporación
    return (numpy.array(deltaFeromonas) + numpy.array(feromonas)) * rho


def heuristica(iteraciones, hormigas):
    #CrearEscenario.crearEscenario(6, 230, 4)
    EscenarioAleatorio.escenarioAleatorio(2, 14, 1, 0.05,0.5, "../")

    # Guardar tiempo inicial
    timerGeneralInicial = time.time()

    #Parametros metaheuristica
    alpha = 1
    beta = 5
    rho = 0.5
    #iteraciones = 50
    #hormigas = 50

    #Leer archivos json
    with open('../Escenarios/Escenarios/Escenario.json') as file:
        data = json.load(file)
        tiempoDesplazamiento = data['tiempoDesplazamiento']
        tiempoAtencion = data['tiempoAtencion']
        tiempoD = data['horasTrabajo']
        numEmpleados = data['numEmpleados']
        numDias = data['numDiasOperacion']
        habEmp = data['habilidadesOperarios']
        habOrde = data['habilidadesOrdenes']
        qParametro = data['porcentajeCumplimientoHabilidades']
        prioridad = data['prioridad']
        costoAns = data['costosANS']
        maxDia = data['maxDia']


    #Calcular tiempo total
    tiempoTotal = []
    for i in range(len(tiempoDesplazamiento)):
        vectorActual = []
        for j in range(len(tiempoDesplazamiento)):
            if (tiempoDesplazamiento[i][j] != 0):
                vectorActual.append(round(tiempoDesplazamiento[i][j] + tiempoAtencion[j],2))
            else:
                vectorActual.append(0)
        tiempoTotal.append(vectorActual)


    #Inicializar feromonas
    feromonas = []
    for i in range(len(tiempoDesplazamiento)):
        feromonas.append(numpy.repeat(1, len(tiempoDesplazamiento)).tolist())


    #Inicializar respuesta
    secuenciaM = []
    valorSecuenciaMax= 0

    p = mp.Pool(iteraciones)

    #Inicio de metaheuristica
    with p:
        #Secuencias de iteración
        secuencias = []
        valorSecuencias = []
        for i in range(hormigas):

            #Reiniciar hormiga
            tiempo = copy.deepcopy(tiempoTotal)
            secuencia = []

            valorSecuencia = 0
            for dias in range(numDias):

                #Auxiliar minMax
                minMax = 999
                for emp in range(numEmpleados):

                    #Reiniciar variables
                    habilidadesEmpleado = habEmp[emp]
                    tiempoDisponible = tiempoD[emp][dias]
                    vacio = True
                    ordenes = 0

                    #En cada recorrido inicio en el nodo 0
                    nodoActual = 0


                    while (vacio or nodoActual != 0):
                        probabilidad = darProbabilidad(tiempo, tiempoDisponible, nodoActual, feromonas, alpha, beta,
                                                       habOrde, habilidadesEmpleado, qParametro)

                        #Determinar nodo a ir
                        aleatorio = random.random()
                        contador = 0

                        while contador < len(probabilidad) and aleatorio > probabilidad[contador]:
                            contador += 1

                        #Probabilidad volver a orden 0
                        if(len(probabilidad)) > 1:
                            if (probabilidad[len(probabilidad) - 1] < aleatorio):
                                contador = 0

                        #Actualizo valores
                        tiempoDisponible -= tiempo[nodoActual][contador]

                        valorSecuencia += 1/(tiempoDesplazamiento[nodoActual][contador]+1)
                        nodoActual = contador



                        #Actualizar valor de la secuencia
                        if(nodoActual!=0):
                            valorSecuencia += prioridad[nodoActual]
                            ordenes += 1
                            if(maxDia[nodoActual] < dias):
                                valorSecuencia -= (dias - maxDia[nodoActual]) * costoAns[nodoActual] * prioridad[nodoActual]


                        secuencia.append(nodoActual)
                        vacio = False

                        #Un nodo no se visita dos veces
                        if(nodoActual!=0):
                            tiempo = borrarNodo(nodoActual, tiempo)

                    if(ordenes < minMax):
                        minMax = ordenes
                valorSecuencia += (minMax + 1) * 0.05

            #Guardar mejor secuencia
            if valorSecuencia > valorSecuenciaMax:
                secuenciaM = secuencia
                valorSecuenciaMax = valorSecuencia


            secuencias.append(secuencia)
            valorSecuencias.append(valorSecuencia)

        #Actualiza feromonas
        feromonas = actualizarFeromonas(secuencias, valorSecuencias, feromonas, rho)

    p.close()

    # ordenesMapa = []
    # ordenesMapa.append(0)
    # for i in secuenciaM:
    #     ordenesMapa.append(i)
    #     ordenesMapa.append(i)
    # print(ordenesMapa)
    # CrearMapa.crearMapa(ordenesMapa, "Test" + str(iteraciones) + "I" + str(hormigas) + "H","Metaheuristica")

    # print("La mejor secuencia es")
    # print(secuenciaM)
    # print("Se pudieron atender " + str(len(secuenciaM) - (numDias * numEmpleados)) + " ordenes de " + str(
    #     len(habOrde) - 1))

    timerGeneralFinal = time.time()
    timerGeneral = timerGeneralFinal - timerGeneralInicial
    # print("La función objetivo tiene un valor de: " + str(valorSecuenciaMax))
    # print("Tiempo de ejecución total: " + str(round(timerGeneral, 2)) + " segundos")

    return (timerGeneral, valorSecuenciaMax)

# print(heuristica(62,10))