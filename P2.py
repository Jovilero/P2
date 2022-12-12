# -*- coding: utf-8 -*-
# Sunday, November 27, 2022 @ 06:47:32 PM
#P2
# JJVL
#%% imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import MicrosecondLocator, DateFormatter, datestr2num
from matplotlib.ticker import FuncFormatter
import datetime
import time
import pandas as pd
from scipy import stats


import misFunciones as mf


#%% Carga de los datos

dic,keys=mf.walkpath('dat')
for each in keys:
    if ('ins' in each.lower() and 'ses0' in each.lower()):
        datosInercial=dic[each]

dic,keys=mf.walkpath('geo')
for each in keys:
    if ('vrs' in each.lower() and 'ses0' in each.lower()):
        VRSgeo=dic[each]

dic,keys=mf.walkpath('kin')
for each in keys:
    if ('vrs' in each.lower() and 'ses0' in each.lower()):
        kinGNSS=dic[each]
    if ('ins' in each.lower() and 'ses0' in each.lower()):
        kinINS=dic[each]

dic,keys=mf.walkpath('aux')
for each in keys:
    if ('vrs' in each.lower() and 'ses0' in each.lower()):
        VRSaux=dic[each]

#dar nombre a las columnas para no trabajr con numeros
datosInercial.columns = ["anyo", "mes", "dia", "hora", "min", "seg", "aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "girX", "girY", "girZ","Roll (deg)", "Pitch (deg)", "Yaw (deg)", "longitud", "latitud", "altura"]
VRSgeo.columns =        ["anyo", "mes", "dia", "hora", "min", "seg", "longitud", "latitud", "altura", "girX", "girY", "girZ", "Roll (deg)", "Pitch (deg)", "Yaw (deg)", "dt(s)",  "num rec"]
VRSaux.columns=         ["anyo", "mes", "dia", "hora", "min", "seg", "longitud", "latitud", "altura",     "ro", "nu" , "N", "xi" ,"eta"  ,  "gN"  ,"gE" ,    "gD"  , "decl"]
kinINS.columns=         ["anyo", "mes", "dia", "hora", "min", "seg", "aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "vN(ms-1)" , "vE(ms-1)"  ,"vD(ms-1)" ,  "Hacc(ms-2)"  , "Hvel(ms-1)"]
kinGNSS.columns=        ["anyo", "mes", "dia", "hora", "min", "seg", "aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "vN(ms-1)" , "vE(ms-1)"  ,"vD(ms-1)" ,  "Hacc(ms-2)"  , "Hvel(ms-1)"]
   

#Columna de fechas
datosInercial['Fecha y hora']=mf.getDateAndTimefromPandasDataframe(datosInercial)
VRSgeo['Fecha y hora']=mf.getDateAndTimefromPandasDataframe(VRSgeo)
kinGNSS['Fecha y hora']=mf.getDateAndTimefromPandasDataframe(kinGNSS)
kinINS['Fecha y hora']=mf.getDateAndTimefromPandasDataframe(kinINS)

#Corrección del desfase en Z por gravedad
datosInercial["aD(ms-2)"]=datosInercial.apply(lambda x: (x["aD(ms-2)"]+9.8),axis=1)


# %%Generacion de las Graficas 
mf.getPlot(VRSgeo,datosInercial,'Fecha y hora',"Roll (deg)", "Pitch (deg)", "Yaw (deg)","GNSS", "INS")
# para abrir la segunda figura es necesario cerrar la primera
mf.getPlot(kinINS,kinGNSS,'Fecha y hora',"aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "INS", "GNSS")
mf.getPlot( datosInercial, kinGNSS,'Fecha y hora',"aN(ms-2)", "aE(ms-2)", "aD(ms-2)", "INS", "GNSS")


           
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
    N=VRSaux['N'][i]
    utm=mf.bfrm2efrm(ang,VRSgeo["latitud"][i],VRSgeo["longitud"][i],VRSgeo["altura"][i],r,p,y,N,dec,bfrm,gps)
    coordenadasCamara.append(utm[3])


#Coordenadas de la camara:
df=pd.DataFrame(coordenadasCamara,columns=["X","Y","Z"])
df.to_csv("Ejercicio2a.csv",sep=',',header=True,encoding="utf-8")
# print(df)

#%%Dibujo de las coordenadas de la camara
mf.kickoutOutLayers(df,"X")
mf.kickoutOutLayers(df,"Y")
mf.kickoutOutLayers(df,"Z")
fig, ax = plt.subplots()
ax.scatter(df["X"], df["Y"], df["Z"], alpha=0.5)
ax.grid(True)
plt.show()


# %%2.b.
