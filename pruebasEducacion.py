# -*- coding: utf-8 -*-
"""
@author: Alexis Sanchez
Fecha: 25 de enero, 2021
Objetivo: Modelar y analizar la situación de las escuelas publicas
          y centros PILARES en la Ciudad de México

Se hara uso de la biblioteca Pandas para manejar los datos extraidos y la 
biblioteca matplotlib para graficar los resultados obtenidos. Asi mismo, se 
tiene un metodo para la lectura de los archivos en forma de csv para crear data 
frames y un metodo que lee el domicilio de la escuela publica y extrae su
alcaldia para mejor procesamiento de los datos. 

"""
import pandas as pd
import matplotlib.pyplot as pl

###########################---INICIAN METODOS----##############################

#Metodo que lee los archivos csv y regresa los dataframes
def leeArchivos():
    publicas=pd.read_csv("C:\\Users\\sanch\\Documents\\Otros\\DataLab\\escuelas-publicas.csv",
                 encoding='UTF-8')
    pilares=pd.read_csv("C:\\Users\\sanch\\Documents\\Otros\\DataLab\\pilares.csv",
                 encoding='UTF-8')
    poblacion=pd.read_csv("C:\\Users\\sanch\\Documents\\Otros\\DataLab\\poblacionAlcaldias.csv",
                 encoding='UTF-8')
    grupos=pd.read_csv("C:\\Users\\sanch\\Documents\\Otros\\DataLab\\gruposAlcaldias.csv",
                 encoding='UTF-8')
    return publicas, pilares,poblacion, grupos

#Metodo que extrae la alcaldia del campo domicilio
def obtenerAlcEscPublicas():
    for index, renglon in publicas.iterrows():
        cad=str(renglon["Domicilio"])
        lista=cad.split(" ")
        alcaldia=""
        if "DELEGACION" in lista:
            indice=lista.index("DELEGACION")
            prev=lista[indice+1]
            alcaldia=prev.replace(',',"").strip()
            if alcaldia=="ALVARO":
                alcaldia+=" OBREGON"
            elif alcaldia=="BENITO":
                alcaldia+=" JUAREZ"
            elif alcaldia=="CUAJIMALPA":
                alcaldia+=" DE MORELOS"
            elif alcaldia=="GUSTAVO":
                alcaldia+=" A. MADERO"
            elif alcaldia=="MIGUEL":
                alcaldia+=" HIDALGO"
            elif alcaldia=="MILPA":
                alcaldia+=" ALTA"
            elif alcaldia=="VENUSTIANO":
                alcaldia+=" CARRANZA"
        else:
            alcaldia="MAGDALENA CONTERAS"
        publicas.at[index,"Alcaldia"]=alcaldia    

#Metodo que crea una grafica, dado el dataframe, el tipo y el titulo     
def generaGrafico(df, tipo, mensaje):
    fig = pl.figure()
    df.plot(kind=tipo)
    fig.suptitle(mensaje,fontsize=16)

def generaImagenTabla(df,size):
    fig, ax=pl.subplots(1,1)
    ax.axis('tight')
    ax.axis('off')
    table=ax.table(cellText=df.values,colLabels=df.columns,loc="center")
    table.set_fontsize(size)
    table.scale(2, 1.5) 
    pl.show()

###########################---TERMINAN METODOS----##############################

#####################---Inicia script de ejecucion---############################

#------1:PROCESAMIENTO--------

#1.1:Se crean los dataframes que se utilizaran en todo el procesamiento
publicas, pilares,poblacion, grupos=leeArchivos()

#1.2:Se procesa el campo de Alcaldia para las escuelas publicas
publicas["Alcaldia"]=""
obtenerAlcEscPublicas()

"""
1.3 Se hace una agregacion usando group by para obtener el numero de escuelas 
publicas y pilares por alcaldia. De igual forma, se generan imagenes con las
tablas donde vienen los datos obtenidos. 

"""
numPorAlcaldiaPub=publicas.groupby(['Alcaldia'])["Alcaldia"].count()
numPilares=pilares.groupby(['ALCALDIA'])['ALCALDIA'].count()

#1.4: A partir de los datos obtenidos, se crean dataframes para manejarlos de mejor forma
dfPublicas = pd.DataFrame({'Alcaldia':numPorAlcaldiaPub.index, 
                           'Numero de escuelas publicas':numPorAlcaldiaPub.values})
dfPilares=pd.DataFrame({'Alcaldia':numPilares.index, 
                        'Numero de pilares':numPilares.values})

#1.5: Se generan dataframes intengrando los datos usando merge sobre el campo Alcaldia
dfPubPil=pd.merge(dfPublicas,dfPilares, on='Alcaldia')
dfHabGrupos=pd.merge(poblacion,grupos,on='Alcaldia')
dfPilaresIds=pd.merge(dfPilares, poblacion,on='Alcaldia')
dfPilaresGrupos=pd.merge(dfPilares,grupos,on='Alcaldia')
dfEscuelasIds=pd.merge(dfPublicas,poblacion,on='Alcaldia')
dfEscuelasGrupos=pd.merge(dfPublicas, grupos,on='Alcaldia')
dfTotal=pd.merge(dfPilaresIds,grupos,on='Alcaldia')
dfTotal=dfTotal.drop(columns=['Preescolar','Productiva'])

dfTotal['Estimacion Numero de Pilares con IDS']=round((((dfTotal['Escolar']+dfTotal['Postproductiva'])*(1-dfTotal['IDS Rezago Educativo']))/(dfTotal['Numero de Habitantes']*dfTotal['IDS']))*1000)
dfTotal["Poblacion Pilares"]=dfTotal['Escolar']+dfTotal['Postproductiva']
dfTotal["Porcentaje Pilares"]=dfTotal['Poblacion Pilares']-dfTotal['Poblacion Pilares']*dfTotal['IDS']
dfTotal["Asignacion Real"]=round(dfTotal["Porcentaje Pilares"]/dfTotal["Porcentaje Pilares"].sum()*260)
dfTotal["Numero Distribucion Pilares"]=round(dfTotal["Estimacion Numero de Pilares con IDS"]/dfTotal["Estimacion Numero de Pilares con IDS"].sum()*260)
dfPorcent=dfPilares
dfPorcent['Porcentaje']=round(dfPorcent['Numero de pilares']/164*100,1)

#dfTotal.to_excel("total.xlsx")

#------Termina Procesamiento

#-------2: RESULTADOS Y GRAFICAS-----------------

#2.1: Se muestran resultados en la consola
print('-----------Numero de escuelas publicas por alcaldia CDMX-------------')
print(numPorAlcaldiaPub) 
print("Total de escuelas publicas: "+str(publicas["Alcaldia"].count()))

print('----------Numero de centros pilares por alcaldia CDMX--------------')
print(numPilares) 
print("Total de pilares: "+str(pilares["ALCALDIA"].count()))

#2.2: Se generan las tablas como imagen para presentacion
generaImagenTabla(dfPublicas,10)
generaImagenTabla(dfPilares,10)
#generaImagenTabla(dfTotal,30)

#2.3: Graficacion Dataframes
"""
Se busca correlacion:
    1. Numero de pilares vs IDS (Indice de Desarrollo Social Ciudad de Mexico)
    2. Numero de pilares vs IDS (Rezago Educativo)
    3. Numero de pilares vs poblacion en edad escolar
    4. Numero de pilares vs poblacion en edad postproductiva (adultos mayores)
    5. Numero de escuelas publicas vs IDS (Indice de Desarrollo Social Ciudad de Mexico)
    6. Numero de escuelas publicas vs IDS (Rezago Educativo)
    7. Numero de escuelas publicas vs poblacion en edad escolar
"""
generaGrafico(numPorAlcaldiaPub,'bar','Numero de escuela publicas por alcaldia')
generaGrafico(numPilares,'bar','Numero de pilares por alcaldia')

dfPubPil.plot(kind='bar',x='Alcaldia',y=['Numero de escuelas publicas','Numero de pilares'])

ax = dfPilaresIds.plot(x='Numero de pilares',y='IDS',kind='scatter',figsize=(10,10))
dfPilaresIds[['Numero de pilares','IDS','Alcaldia']].apply(lambda x: ax.text(*x),axis=1)

ax2 = dfPilaresIds.plot(x='Numero de pilares',y='IDS Rezago Educativo',kind='scatter',figsize=(10,10))
dfPilaresIds[['Numero de pilares','IDS Rezago Educativo',
              'Alcaldia']].apply(lambda x: ax2.text(*x),axis=1)

ax3 = dfPilaresGrupos.plot(x='Numero de pilares',y='Escolar',kind='scatter',figsize=(10,10))
dfPilaresGrupos[['Numero de pilares','Escolar',
                 'Alcaldia']].apply(lambda x: ax3.text(*x),axis=1)

ax4 = dfPilaresGrupos.plot(x='Numero de pilares',y='Postproductiva',kind='scatter',figsize=(10,10))
dfPilaresGrupos[['Numero de pilares','Postproductiva',
                 'Alcaldia']].apply(lambda x: ax4.text(*x),axis=1)

ax5 = dfEscuelasIds.plot(x='Numero de escuelas publicas',y='IDS',kind='scatter',figsize=(10,10))
dfEscuelasIds[['Numero de escuelas publicas','IDS',
               'Alcaldia']].apply(lambda x: ax5.text(*x),axis=1)

ax6 = dfEscuelasIds.plot(x='Numero de escuelas publicas',y='IDS Rezago Educativo',kind='scatter',figsize=(10,10))
dfEscuelasIds[['Numero de escuelas publicas','IDS Rezago Educativo',
               'Alcaldia']].apply(lambda x: ax6.text(*x),axis=1)

ax7 = dfEscuelasGrupos.plot(x='Numero de escuelas publicas',y='Escolar',kind='scatter',figsize=(10,10))
dfEscuelasGrupos[['Numero de escuelas publicas','Escolar',
                 'Alcaldia']].apply(lambda x: ax7.text(*x),axis=1)
ax8 = dfTotal.plot(x='Numero Distribucion Pilares',y='IDS',kind='scatter',figsize=(10,10))
dfTotal[['Numero Distribucion Pilares','IDS',
                 'Alcaldia']].apply(lambda x: ax8.text(*x),axis=1)
ax9 = dfTotal.plot(x='Asignacion Real',y='Poblacion Pilares',kind='scatter',figsize=(10,10))
dfTotal[['Asignacion Real','Poblacion Pilares',
                 'Alcaldia']].apply(lambda x: ax9.text(*x),axis=1)
ax10 = dfTotal.plot(x='Asignacion Real',y='Poblacion Pilares',kind='scatter',figsize=(10,10))
dfTotal[['Asignacion Real','Poblacion Pilares',
                 'Alcaldia']].apply(lambda x: ax10.text(*x),axis=1)
#-----Fin de Resultados y Graficas

#-----Fin de script de ejecucion