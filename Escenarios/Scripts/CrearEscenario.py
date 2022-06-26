import json
import math
from datetime import datetime
import numpy

def crearEscenario(numEmpleados, numOrdenes, numDias, costoAns, path):

    data = {}
    data['numEmpleados'] = numEmpleados
    data['numOrdenes'] = numOrdenes - 1
    data['numDiasOperacion'] = numDias

    tiempoDesplazamiento = []
    habilidades = []
    tiempoAtencion = 0
    contadorTiempoA = 0

    stageFile = open(path + 'Escenarios/Jsons/Ordenes.json')
    stageData = json.load(stageFile)
    print (len(stageData))


    contador = 0
    while numOrdenes > (contador):
        row = stageData[contador]

        # Sacar el número de habilidades
        if len(habilidades) == 0:
            habilidades.append(row['Skills'][0])
        else:
            esta = True
            for i in habilidades:
                if i == row['Skills'][0]:
                    esta = False
            if esta:
                habilidades.append(row['Skills'][0])

        #Calcular tiempo
        distanciaA = []
        tiempoA = []
        contadorDis = 0
        while (contadorDis) < numOrdenes:
            comparar = stageData[contadorDis]
            if(contadorDis ==contador):
                distanciaA.append(0)
                tiempoA.append(0)
            else:
                lat1 = row['Latitude']
                long1 = row['Longitude']
                lat2 = comparar['Latitude']
                long2 = comparar['Longitude']

                c = math.pi / 180
                d = 2 * 6371 * math.asin(math.sqrt(math.sin(c * (lat2 - lat1) / 2) ** 2 + math.cos(c * lat1)
                                                * math.cos(c * lat2) * math.sin(c * (long2 - long1) / 2) ** 2))
                distanciaA.append(d)
                tiempoA.append((d + 10)/ 24)

            contadorDis += 1
        contador += 1

        tiempoDesplazamiento.append(tiempoA)

    data['numHabilidades'] = len(habilidades)
    data['tiempoDesplazamiento'] = tiempoDesplazamiento


    tiempoDeAtencion = []
    contador = 0
    habilidadesOrdenes = []

    empleadosFile = open(path+"Escenarios/Jsons/Empleados.json")
    empleadosData = json.load(empleadosFile)


    for empleado in empleadosData:
        if len(empleado['Tasks']) > 0:
            tasks = empleado['Tasks']
            for task in tasks:
                minutos = int(task['DateEndTime'][14:16]) - int(task['DateStartAttention'][14:16])
                horas = int(task['DateEndTime'][11:13]) - int(task['DateStartAttention'][11:13])
                tiempoAtencion += (minutos + horas * 60)
                contadorTiempoA += 1
    tiempoAtencion = tiempoAtencion / (contadorTiempoA * 60)


    maxDia = []
    hoy = datetime.strptime(stageData[0]['DateSolutionlimit'],'%Y-%m-%dT%H:%M:%S')

    prioridad = []
    # Extraer habilidades ordenes
    while numOrdenes > contador:
        tiempoDeAtencion.append(tiempoAtencion)
        row = stageData[contador]


        #Asignar maximo dia de atención a la orden
        diaActual = datetime.strptime(row['DateSolutionlimit'],'%Y-%m-%dT%H:%M:%S')
        deltaDias = (diaActual-hoy).days
        maxDia.append(deltaDias)

        # Extraer habilidades de empleados
        habilidadesOrd = []
        habilidadO = row['Skills']
        contadorH = 0
        for habilidad in habilidades:
            habilidadesOrd.append(0)
            for h in habilidadO:
                if habilidad == h:
                    habilidadesOrd[contadorH] = 1
            contadorH += 1
        contador += 1
        habilidadesOrdenes.append(habilidadesOrd)

        #Asignar si la orden es prioritaria
        if(row['IsPriority']):
            prioridad.append(1.1)
        else:
            prioridad.append(1)

    contadorE = 0

    habilidadesEmpleados = []
    horasDisponible = []
    while contadorE < numEmpleados:

        # Extraer habilidades de empleados
        habilidadesEmpl = []
        habilidadE = empleadosData[contadorE]['Skills']
        contadorH = 0
        for habilidad in habilidades:
            habilidadesEmpl.append(0)
            for h in habilidadE:
                if habilidad == h:
                    habilidadesEmpl[contadorH] = 1
            contadorH += 1
        contadorE += 1
        habilidadesEmpleados.append(habilidadesEmpl)


        #Extraer horas disponible empledo
        contadorDias = 0
        horasE = []
        while contadorDias < numDias:
            diaActual = empleadosData[contadorE]['Availability'][contadorDias]
            horasE.append((int(diaActual['EndTime'][0:2]) - int(diaActual['StartTime'][0:2]) - 1))
            contadorDias += 1
        horasDisponible.append(horasE)

    data['tiempoAtencion'] = tiempoDeAtencion
    data['habilidadesOperarios'] = habilidadesEmpleados
    data['habilidadesOrdenes'] = habilidadesOrdenes
    data['porcentajeCumplimientoHabilidades'] = 1
    data['horasTrabajo'] = horasDisponible
    data['maxDia'] = maxDia
    costoAns = numpy.repeat(costoAns,numOrdenes-1).tolist()
    costoAns.insert(0,0)
    data['costosANS'] = costoAns
    data['prioridad'] = prioridad

    with open(path + "Escenarios/Escenarios/Escenario.json", 'w') as file:
        json.dump(data,file)


# crearEscenario(6,231,6,0.05)

