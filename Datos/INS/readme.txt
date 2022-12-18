DESCRIPCIÓN DEL CONTENIDO DE LOS FICHEROS


.txt
----

Este fichero contiene los datos tal como son exportados por la aplicación SGBcenter, cabercera incluida

.dat
----

Este fichero contiene los mismos datos que el fichero .txt pero en forma de matriz numérica y sin cabecera, para facilitar su carga en Matlab, Python, etc. 

.aux
----

Este fichero, que coincide secuencialmente con el .dat, contiene los siguientes datos auxiliares


 UTC date       UTC time   latitud(deg)   longitud(deg)  h(elip)     ro(m)        nu(m)          N(m)   xi(") eta(")    gN (m/s2)  gE (m/s2)    gD (m/s2)   decl.m.(deg)
----------   ------------  ------------  -------------  --------  -----------   -----------     -------  ----- -----  ------------  ----------  ----------  -----------
YYYY MM DD   hh mi ss.sss

2021 10 21   15 28 46.000   39.48142700   -0.33657300    62.302   6361245.827   6386785.409      50.019  -3.1   4.1    -0.00000049  0.00000000  9.80104494    1.050000

ro -> radio de curvatura terrestre correspondiente a la sección normal meridiana (az = 0º ó az = 180º)
nu -> radio de curvatura terrestre correspondiente a la sección normal del primer vertical (az = 90º ó az = 270º)
N -> ondulación del geoide para obtener la altitud ortométrica H = h - N
xi -> componente de la desviación de la vertical en dirección del meridiano expresada en segundos sexagesimales
eta -> componente de la desviación de la vertical en dirección del primer vertical expresada en segundos sexagesimales
gN,gE,gD -> componentes del vector de gravedad expresadas en el n-frame
decl.m -> declinación magnetica en grados sexagesimales (IGRF)

.kin
----
Este fichero, cuya frecuencia es de 1 Hz (1 dato por segundo), contiene los vectores de aceleración y velocidad
deducidos de las posiciones proporcionadas por el receptor GPS del SBG-Ellipse N

 UTC date       UTC time    aN(ms-2) aE(ms-2)   aD(ms-2)  vN(ms-1)  vE(ms-1)  vD(ms-1)   Hacc(ms-2)   Hvel(ms-1)
----------   ------------  --------  --------   -------   -------   -------   -------    ----------   ---------- 
YYYY MM DD   hh mi ss.sss

2022 10 20   15 30 32.000    -0.333    -0.172     0.298    -1.665    -0.774     0.048      0.375         1.837

aN(m),aE(m),aD(m) -> componentes del vector de aceleración expresadas en el sistema de navegación
vN(m),vE(m),vD(m) -> componentes del vector de velocidad expresadas en el sistema de navegación
Hacc -> aceleración horizontal
Hvel -> velocidad horizontal

.fig
----
Fichero gráfico de Matlab para el análisis visual de los datos. Puede editarse, hacer zoom, etc.




