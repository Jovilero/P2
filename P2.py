# -*- coding: utf-8 -*-
# Saturday, December 17, 2022 @ 06:52:33 PM
# P2
# JJVL
#%% imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import MicrosecondLocator, DateFormatter, datestr2num
from matplotlib.ticker import FuncFormatter
import datetime
import pandas as pd

import misFunciones as mf


#%% Carga de los datos
sesion='ses4re'

datosInercial=pd.read_csv(fr'.\Datos\INS\INS-20-10-2022_{sesion}.dat',delim_whitespace=True, header=None)
kinINS=pd.read_csv(fr'.\Datos\INS\INS-20-10-2022_{sesion}.kin',delim_whitespace=True, header=None)
INSaux=pd.read_csv(fr'.\Datos\INS\INS-20-10-2022_{sesion}.aux',delim_whitespace=True, header=None)
VRSgeo=pd.read_csv(fr'.\Datos\GNSS\Unified\VRS-20-10-2022_{sesion}.geo',delim_whitespace=True, header=None)
kinGNSS=pd.read_csv(fr'.\Datos\GNSS\Unified\VRS-20-10-2022_{sesion}.kin',delim_whitespace=True, header=None)
VRSaux=pd.read_csv(fr'.\Datos\GNSS\Unified\VRS-20-10-2022_{sesion}.aux',delim_whitespace=True, header=None)

#dar nombre a las columnas para no trabajr con numeros
datosInercial.columns = ["anyo", "mes", "dia", "hora", "min", "seg", "aX(ms-2)", "aY(ms-2)", "aZ(ms-2)", "girX", "girY", "girZ","Roll (deg)", "Pitch (deg)", "Yaw (deg)", "longitud", "latitud", "altura"]
kinINS.columns=         ["anyo", "mes", "dia", "hora", "min", "seg", "aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "vN(ms-1)" , "vE(ms-1)"  ,"vD(ms-1)" ,  "Hacc(ms-2)"  , "Hvel(ms-1)"]
kinGNSS.columns=        ["anyo", "mes", "dia", "hora", "min", "seg", "aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "vN(ms-1)" , "vE(ms-1)"  ,"vD(ms-1)" ,  "Hacc(ms-2)"  , "Hvel(ms-1)"]
INSaux.columns=         ["anyo", "mes", "dia", "hora", "min", "seg", "longitud", "latitud", "altura",     "ro", "nu" , "N", "xi" ,"eta"  ,  "gN"  ,"gE" ,    "gD"  , "decl"]
VRSgeo.columns =        ["anyo", "mes", "dia", "hora", "min", "seg", "longitud", "latitud", "altura", "girX", "girY", "girZ", "Roll (deg)", "Pitch (deg)", "Yaw (deg)", "dt(s)",  "num rec"]
VRSaux.columns=         ["anyo", "mes", "dia", "hora", "min", "seg", "longitud", "latitud", "altura",     "ro", "nu" , "N", "xi" ,"eta"  ,  "gN"  ,"gE" ,    "gD"  , "decl"]

#Columna de fechas
datosInercial['Fecha y hora']=mf.getDateAndTimefromPandasDataframe(datosInercial)
VRSgeo['Fecha y hora']       =mf.getDateAndTimefromPandasDataframe(VRSgeo)
kinGNSS['Fecha y hora']      =mf.getDateAndTimefromPandasDataframe(kinGNSS)
kinINS['Fecha y hora']       =mf.getDateAndTimefromPandasDataframe(kinINS)
 
#correccion del desfase temporal del tiempo UTC-GPS (18 segundos) en los datos del Inercial
datosInercial["Fecha y hora"]=datosInercial.apply(lambda x: (x["Fecha y hora"]+datetime.timedelta(seconds=18)),axis=1)

#Obtención de las aceleraciones  del inercial
for i in range(len(datosInercial.index)):
    n,e,d=mf.aceleracionesInercial(datosInercial["Roll (deg)"][i], datosInercial["Pitch (deg)"][i], datosInercial["Yaw (deg)"][i], datosInercial["aX(ms-2)"][i], datosInercial["aY(ms-2)"][i], datosInercial["aZ(ms-2)"][i])
    if i == 0:
        #creacion de las columnas de las aceleraciones Northing, easting, down.
        datosInercial.insert(i,"aN(ms-2)",n+INSaux["gN"][i])
        datosInercial.insert(i,"aE(ms-2)",e+INSaux["gE"][i])
        datosInercial.insert(i,"aD(ms-2)",d+INSaux["gD"][i])
    else:
        #Corrección del desfase en Z por gravedad Northing, easting, down
        datosInercial["aN(ms-2)"][i]=n+INSaux["gN"][i]
        datosInercial["aE(ms-2)"][i]=e+INSaux["gE"][i]
        datosInercial["aD(ms-2)"][i]=d+INSaux["gD"][i]



#%% 1 - Generacion de las Graficas 
mf.getPlot(VRSgeo,datosInercial,'Fecha y hora',"Roll (deg)", "Pitch (deg)", "Yaw (deg)","GNSS", "INS")
mf.getPlot(kinINS,kinGNSS,'Fecha y hora',"aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "INS", "GNSS")
mf.getPlot(datosInercial, kinGNSS,'Fecha y hora',"aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "INS", "GNSS")


#%% 2.a. 
# Se asume que las coordenadas contenidas en el fichero vrs*.geo han sido promediadas entre los 4 receptores 
# y hacen referencia al promedio de la posicion de los 4 receptores GNSS sobre plataforma rigida. Dicha posicion promediada coincide en coordenadas con el dispositivo inercial.
# atendiendo a esto, y el croquis proporcionado, la posición de la camara desde la posición promediada de los 4 receptores
# se diferencia en b-frame respecto al dispositivo inercial 0,7060 metros en dirección x1.
# La posición por tanto de la camara respecto de las coordenadas en el fichero seran las coordenadas del fichero + un 
# incremento constante de x1 equivalente a 0,706, más los incrementos de posición hasta el centro de proyección de la misma
# se asume por tanto que el 0,0,0 de la plataforma coincide con las coordenadas gps obtenidas del fichero vrs.geo

#deficion de la situacion del bframe
ang = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
bfrm = np.array([[0,0,-0.014,0.72],[0,0,0,-0.018],[0,0,-0.01,-0.495]])
gps = np.array([[0],[0],[0]])

coordenadasCamara=[]

for i in range(len(VRSgeo.index)):

    r = datosInercial["Roll (deg)"][i]
    p = datosInercial["Pitch (deg)"][i]
    y = datosInercial["Yaw (deg)"][i]
    dec = VRSaux["decl"][i]
    n=VRSaux['N'][i]
    utm=mf.bfrm2efrm(ang,VRSgeo["latitud"][i],VRSgeo["longitud"][i],VRSgeo["altura"][i],r,p,y,n,dec,bfrm,gps)
    coordenadasCamara.append(utm[3])


#Coordenadas de la camara:
XYZcamara=pd.DataFrame(coordenadasCamara,columns=["X","Y","Z"])
mf.kickoutOutLayers(XYZcamara,"X")
mf.kickoutOutLayers(XYZcamara,"Y")
mf.kickoutOutLayers(XYZcamara,"Z")

XYZcamara.to_csv(fr"Ejercicio2a_{sesion}.csv",sep=',',header=True,encoding="utf-8")
# print(df)

fig, ax = plt.subplots()
ax.scatter(XYZcamara["X"], XYZcamara["Y"], XYZcamara["Z"], alpha=0.5)
ax.grid(True)
plt.show()


#%%2.b.
dif_velocidades=[[[0],[0],[0]]]
velocidades=[[0,0,0]]
coordenadas=[[INSaux["latitud"][0],INSaux["longitud"][0],INSaux["altura"][0]]]
for i in range(len(datosInercial.index)):
    n,e,d=mf.aceleracionesInercial(datosInercial["Roll (deg)"][i], datosInercial["Pitch (deg)"][i], datosInercial["Yaw (deg)"][i], datosInercial["aX(ms-2)"][i], datosInercial["aY(ms-2)"][i], datosInercial["aZ(ms-2)"][i])
    aN=n+INSaux["gN"][i]
    aE=e+INSaux["gE"][i]
    aD=d+INSaux["gD"][i]
    
    if i == 0:
        difLatitud, difLongitud, difH = mf.dif_Posicion(coordenadas[i][0],coordenadas[i][1],velocidades[i][0],velocidades[i][1],velocidades[i][2],INSaux["ro"][i],INSaux["nu"][i])
        nuevaLatitud=INSaux["latitud"][i]+difLatitud
        nuevaLongitud=INSaux["longitud"][i]+difLongitud
        nuevaAltura=INSaux["altura"][i]+difH
    if i!=0:
        difLatitud, difLongitud, difH = mf.dif_Posicion(nuevaLatitud,nuevaAltura,vN,vE,vD,INSaux["ro"][i],INSaux["nu"][i])
        nuevaLatitud=coordenadas[i-1][0]+difLatitud
        nuevaLongitud=coordenadas[i-1][1]+difLongitud
        nuevaAltura=coordenadas[i-1][1]+difH
    
    array_velocidades_ti=mf.ecuInercialLibre(coordenadas[i-1][0],difLatitud,difLongitud, aN, aE, aD, velocidades[i-1][0],velocidades[i-1][1],velocidades[i-1][2], INSaux["gN"][i], INSaux["gE"][i], INSaux["gD"][i],0)
    dif_velocidades.append(array_velocidades_ti)
    vN=velocidades[i-1][0]+dif_velocidades[i][0][0]
    vE=velocidades[i-1][1]+dif_velocidades[i][1][0]
    vD=velocidades[i-1][2]+dif_velocidades[i][2][0]
    
    if i!=0:
        velocidades.append([vN,vE,vD])
        coordenadas.append([nuevaLatitud,nuevaLongitud,nuevaAltura])

#Creación del fichero de coordenadas geodesicas obtenidas del inercial
latlonInercial=pd.DataFrame(coordenadas,columns=["lat","lon","h"])
latlonInercial.to_csv("latlon2b_inercial.csv",sep=',',header=True,encoding="utf-8")

#deficion de la situacion del bframe
ang = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
bfrm = np.array([[0,0,-0.014,0.72],[0,0,0,-0.018],[0,0,-0.01,-0.495]])
ins = np.array([[0],[0],[0]])

coordenadasCamara=[]

for i in range(len(datosInercial.index)):

    r = datosInercial["Roll (deg)"][i]
    p = datosInercial["Pitch (deg)"][i]
    y = datosInercial["Yaw (deg)"][i]
    dec = INSaux["decl"][i]
    n=INSaux['N'][i]
      
    utm=mf.bfrm2efrm(ang,latlonInercial["lat"][i],latlonInercial["lon"][i],latlonInercial["h"][i],r,p,y,n,dec,bfrm,ins)
   
    if str(i).endswith('0'):
        print(i)
    coordenadasCamara.append(utm[3])

#Coordenadas de la camara:
XYZcamara=pd.DataFrame(coordenadasCamara,columns=["X","Y","Z"])

XYZcamara.to_csv("Ejercicio2b_inercial.csv",sep=',',header=True,encoding="utf-8")
# print(df)
#%%%
fig, ax = plt.subplots()
ax.scatter(XYZcamara["X"], XYZcamara["Y"], XYZcamara["Z"], alpha=0.5)
ax.grid(True)
plt.show()

# %%
