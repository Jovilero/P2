# -*- coding: utf-8 -*-
# Sunday, October 30, 2022 @ 05:22:46 PM
# JJVL
import os
import numpy  as np
import math   as m
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from scipy import stats
import pyproj as pj

def r1(a):
    #Matriz de rotación para el eje alfa
    R1 = np.array([[1,0,0],[0,m.cos(a),m.sin(a)],[0,-m.sin(a),m.cos(a)]])
    return R1

def r2(b):
    #Matriz de rotación para el eje beta
    R2 = np.array([[m.cos(b),0,-m.sin(b)],[0,1,0],[m.sin(b),0,m.cos(b)]])
    return R2

def r3(g):
    #Matriz de rotación para el eje gamma
    R3 = np.array([[m.cos(g),m.sin(g),0],[-m.sin(g),m.cos(g),0],[0,0,1]])
    return R3

def rot_mat(a,b,g):
    #Matriz de rotación estandar de los tres ejes
    rotacion = np.array([[m.cos(g),m.sin(g),0],[-m.sin(g),m.cos(g),0],[0,0,1]]).dot(np.array([[m.cos(b),0,-m.sin(b)],[0,1,0],[m.sin(b),0,m.cos(b)]])).dot(np.array([[1,0,0],[0,m.cos(a),m.sin(a)],[0,-m.sin(a),m.cos(a)]]))
    return rotacion

def rot_ne(lat,lon):
    #Matriz de rotación estandar
    rotacion = np.array([[m.cos(-lon),m.sin(-lon),0],[-m.sin(-lon),m.cos(-lon),0],[0,0,1]]).dot(np.array([[m.cos(lat+m.pi/2),0,-m.sin(lat+m.pi/2)],[0,1,0],[m.sin(lat+m.pi/2),0,m.cos(lat+m.pi/2)]]))
    return rotacion

def gms_to_gd(valor):
    if str(valor).isnumeric():
        grados = m.trunc(valor)

        minutos = m.modf(valor)[0]*60
    
        segundos = m.modf(minutos)[0]*60
    
        if (minutos < 0 or segundos < 0):
            return "-"+str(grados)+'º'+str(int(abs(minutos)))+"'"+str(round(abs(segundos),5))+"''"
        
        return str(grados)+'º'+str(int(minutos))+"'"+str(round(segundos,5))+"''"



pd.options.display.float_format = "{:.4f}".format

    
    
  
def File2Pandas(path):
    pa=pd.read_fwf(fr'{path}',index=False, header=None)
    return pa


def getPlot(datos1,datos2,x,y1,y2,y3='',linea1='',linea2='',title=''):
    fig, axs = plt.subplots(3,1)
    if title!='':
        axs[0].set_title(title)
    
    #remover outliers
    kickoutOutLayers(datos1,y1)
    kickoutOutLayers(datos1,y2)
    kickoutOutLayers(datos1,y3)
    # kickoutOutLayers(datos2,y1)
    # kickoutOutLayers(datos2,y2)
    # kickoutOutLayers(datos2,y3)


    axs[0].set_title(f'{y1}, {y2}, {y3} según Inercial y GNSS-VRS')

    datos1[y1]=np.where(datos1[y1]==0, np.nan,datos1[y1])
    datos2[y1]=np.where(datos2[y1]==0, np.nan,datos2[y1])
    axs[0].plot(datos1[x], datos1[y1], datos2[x], datos2[y1], linewidth=0.45)
    

    datos1[y2]=np.where(datos1[y2]==0, np.nan,datos1[y2])
    datos2[y2]=np.where(datos2[y2]==0, np.nan,datos2[y2])
    axs[1].plot(datos1[x], datos1[y2], datos2[x], datos2[y2], linewidth=0.45)
  
    datos1[y3]=np.where(datos1[y3]==0, np.nan,datos1[y3])
    datos2[y3]=np.where(datos2[y3]==0, np.nan,datos2[y3])
    axs[2].plot(datos1[x], datos1[y3], datos2[x], datos2[y3], linewidth=0.45)

    axs[2].set_xlabel(f'{x}')
    axs[0].set_ylabel(f'{y1}')
    axs[1].set_ylabel(f'{y2}')
    axs[2].set_ylabel(f'{y3}')

    axs[0].grid()
    axs[1].grid()
    axs[2].grid()

    axs[0].legend([f'{linea1} {y1}', f'{linea2} {y1}'])
    axs[1].legend([f'{linea1} {y2}', f'{linea2} {y2}'])
    axs[2].legend([f'{linea1} {y3}', f'{linea2} {y3}'])
    
    return plt.show()

def getDateAndTimefromPandasDataframe(pandasdataframe):
    pandasdataframe['strtime']=pandasdataframe.apply(lambda x: '%i:%i:%s' % (x[3],x[4],x[5]), axis=1)
    pandasdataframe['Fecha y hora']=pandasdataframe.apply(lambda x: datetime.datetime.strptime(x['strtime'], '%H:%M:%S.%f'),axis=1)
    return pandasdataframe['Fecha y hora']

def kickoutOutLayers(pandasdataframe,column):
    """Remueve outliers con z-score 2.5

    Args:
        pandasdataframe (_type_): _description_
        column (_type_): _description_
    """
    pandasdataframe[column]=np.where(np.abs(stats.zscore(pandasdataframe[column]))<3,pandasdataframe[column],np.nan)



def bfrm2efrm(ang,lat,lon,h,r,p,y,N,dec,xbfrm,xbgps):
    ang_m = pd.DataFrame(ang,columns=['alpha(º)','beta(º)','gamma(º)'],index=['PLA','GPS','INS','CAM'])
    bfrm_m = pd.DataFrame(xbfrm,index=['x1(m)','x2(m)','x3(m)'],columns=['PLA','GPS','INS','CAM']).T
    lla_m = []
    lla_m2 = []
    utm = []
    
    # Calculamos matriz Cinsb
    Cinsb = rot_mat(m.radians(ang[2][0]),m.radians(ang[2][1]),m.radians(ang[2][2])).T
    # Calculamos matriz Cnins
    Cnins = rot_mat(m.radians(-r),m.radians(-p),m.radians(-y))
    # Declinacion
    r33 = r3(m.radians(-dec))
    
    # Calculamos matriz Cen
    Cen = rot_ne(m.radians(lon),m.radians(lat))
    # Coodenadas xgegps
    trans = pj.Transformer.from_crs(4326,4978)
    x,y,z = trans.transform(lat,lon,h-N)
    xgegps = np.array([[x],[y],[z]])
    # XE y coordenadas ECEF

    # xe=xegps+cen * cnins* cinsb(xb-xbgps)
    # del norte magnetico al norte geográfico
    xe = np.add(xgegps,Cen.dot(r33).dot(Cnins).dot(Cinsb).dot(np.subtract(xbfrm,xbgps)))
    XYZecef = pd.DataFrame(xe,index=['X(m)','Y(m)','Z(m)'],columns=['PLA','GPS','INS','CAM']).T
    
    #Coordenadas Geodesicas
    ecef = pj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    for i in range(len(xe)+1):
        ln, lt, alt = pj.transform(ecef, lla, xe[0][i], xe[1][i], xe[2][i], radians=False)
        # print(ln,lt,alt)
        lla_m.append([gms_to_gd(lt),gms_to_gd(ln),alt])
        lla_m2.append([ln,lt,alt])
    geod = pd.DataFrame(lla_m,columns=['Latitud','Longitud','h(m)'],index=['PLA','GPS','INS','CAM'])
    #Obtención de las coordenadas UTM
    trans2 = pj.Transformer.from_crs("epsg:4326","+proj=utm +zone=30 +ellps=WGS84",always_xy=True)
    for i in range(len(lla_m2)):
        xx,yy,zz = trans2.transform(lla_m2[i][1],lla_m2[i][0],lla_m2[i][2])
        utm.append([xx,yy,zz])
    XYZutm = pd.DataFrame(utm,columns=['x(m)','y(m)','Z(m)'],index=['PLA','GPS','INS','CAM'])
    # print(tm)
    return utm
    

def aceleracionesInercial(r,p,y,aX,aY,aZ):
    aceleracionesNED = rot_mat(m.radians(-r),m.radians(-p),m.radians(-y)).dot(np.array([[aX],[aY],[aZ]])).T
    
    return aceleracionesNED[0][0],aceleracionesNED[0][1], aceleracionesNED[0][2]

def dif_Posicion(latitud,h,vN,vE,vD,ro,nu):
    difLatitud=vN*0.02/(ro+h)
    difLongitud=(vE*0.02/(nu+h))*np.cos(latitud)
    difH=-vD*0.02
    return difLatitud, difLongitud, difH

def ecuInercialLibre(latitud,dif_latitud,dif_longitud,aN, aE, aD, vN, vE, vD, gN, gE, gD, we):
    
    dif_vN=aN+gN+2*we*vE*np.sin(latitud)+dif_latitud*vD-dif_longitud*np.sin(latitud)*vE
    dif_vE=aE+gE+2*we*np.sin(latitud)*vN+2*we*np.cos(latitud)*vD+dif_longitud*np.sin(latitud)*vN+dif_longitud*np.cos(latitud)*vD
    dif_vD=aD+gD+2*we*np.cos(latitud)*vE-dif_longitud*np.cos(latitud)*vE-dif_latitud*vN

    return np.array([[dif_vN*0.02],[dif_vE*0.02],[dif_vD*0.02]])
    
