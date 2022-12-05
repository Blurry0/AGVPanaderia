import json
import boto3
from decimal import Decimal
from io import StringIO, BytesIO
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plotear2datos(x,y,nombre_x, nombre_y,tienda,fecha,bucket):

    plt.cla()
    plt.clf()
    
    plt.figure(figsize=(12, 9))

    #Plot Bar
    bar=plt.bar(x, y, color= "#8bd3c7")
    for p in bar:
        height = p.get_height()
        plt.text(x=p.get_x() + p.get_width() / 2, y=height+.10,
        s="{}".format(height),
        ha='center',
        fontdict= {'family': 'arial',
            'color':  'black',
            'weight': 'normal',
            'size': 12
            })
    plt.title('Tienda '+tienda+': '+ nombre_x + ' vs '+nombre_y)
    plt.xlabel(nombre_x)
    plt.ylabel(nombre_y)
    titulo='Tienda'+tienda+'/'+fecha+'/'+ nombre_y +'.png'
    save_image(plt,titulo,bucket)

def plotear3datos(dias,bolillo,concha,orejita,panque,dona,nombre,bucket):

    plt.cla()
    plt.clf()
    
    colores = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
    X_axis = np.arange(len(dias))

    bar1=plt.bar(X_axis - 0.3, bolillo, 0.15, label = 'Bolillo', color = colores[0])
    bar1+=plt.bar(X_axis - 0.15, concha, 0.15, label = 'Concha', color = colores[1])
    bar1+=plt.bar(X_axis , orejita, 0.15, label = 'Orejita', color = colores[2])
    bar1+=plt.bar(X_axis + 0.15, panque, 0.15, label = 'Muffin', color = colores[3])
    bar1+=plt.bar(X_axis + 0.3, dona, 0.15, label = 'Dona', color = colores[4])

    for p in bar1:
        height = p.get_height()
        if height != 0:
            plt.text(x=p.get_x() + p.get_width() / 2, y=height+.10,
            s="{}".format(height),
            ha='center',
            fontdict= {'family': 'arial',
            'color':  'black',
            'weight': 'normal',
            'size': 12
            })
        
    plt.xticks(X_axis, dias)
    plt.xlabel("Fechas")
    plt.ylabel(nombre)
    plt.title(nombre+" historica de panes")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    titulo = 'Historico/'+ nombre + '.png'
    save_image(plt,titulo,bucket)

def save_image(plt,titulo,bucket):
    out_key='Graficas/' + titulo
    #Save to image
    img_data = BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight')
    img_data.seek(0)

    #Put plot in S3 bucket
    bucket.put_object(Body=img_data, ContentType='image/png', Key=out_key)

def lambda_handler(event, context):
    
    
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    table = dynamodb.Table('Compras')
    inventario = dynamodb.Table('Inventario')
    bucket = boto3.resource('s3').Bucket('panaderia-equipo5')
    
    #Declaring arrays
    tipo_pan=["Bolillo","Muffin","Dona","Orejita","Concha"]
    cantidad_pan=[0,0,0,0,0]
    precio_pan=[0,0,0,0,0]
    
    
    with table.batch_writer() as batch:
        for i in range(len(event['Compras'])):
            print(int(event["ts"]))
            
            #Add item to table Compras
            batch.put_item(
                Item={
                    "Pan":event["Compras"][i]['Pan'],
                    "ts":int(event["ts"]),
                    "Precio":Decimal(event["Compras"][i]['Precio']),
                    "Fecha":event["Compras"][i]['Fecha'],
                    "Cantidad":event["Compras"][i]['Can']
                }
            )
            
            #Decrease item to table Inventario
            inventario.update_item(
                Key={
                    'Pan': event["Compras"][i]['Pan']  
                },
                UpdateExpression="set Cantidad = Cantidad - :val",
                ExpressionAttributeValues={
                    ':val':int(event["Compras"][i]['Can'])
                }
            )
            
            #Save information for plotting
            index_pan=tipo_pan.index(event["Compras"][i]['Pan'])
            cantidad_pan[index_pan]=event["Compras"][i]['Can']
            precio_pan[index_pan]=float(event["Compras"][i]['Precio'])*int(event["Compras"][i]['Can'])
    
    print("Tipo de Pan")
    tipo_pan=np.array(tipo_pan, dtype=np.dtype('U9'))
    print(tipo_pan)
    print("Cantidad de Pan")
    cantidad_pan=np.array(cantidad_pan, dtype=np.uint8)
    print(cantidad_pan)
    print("Precio de Pan")
    precio_pan=np.array(precio_pan, dtype=np.float16)
    print(precio_pan)
    print("Numero de tienda")
    tienda = event["Tienda"]
    print(tienda)
    
    
    plotear2datos(tipo_pan,cantidad_pan,'Panes','Cantidad',str(tienda),event["Compras"][0]['Fecha'],bucket)
    plotear2datos(tipo_pan,precio_pan,'Panes','Precio',str(tienda),event["Compras"][0]['Fecha'],bucket)
    
    
    if tienda == 3:
        print("Historico")
        #Realizar ploteado Historico
        #Guardamos los datos obtenidos del scan en un DataFrame
        historico = table.scan()['Items']
        data=pd.json_normalize(historico)
        print(data)
        
        #Obtenemos las fechas almacenadas guardando unicamente un valor unico
        fechas = np.unique(data['Fecha'].to_numpy())
        print("Fechas")
        print(fechas)
        print("Panes por fechas")
        #Loop para pasar por todas las fechas
        print("Tipo Pan")
        cantidad_historico_panes = []
        precio_historico_panes = []
        for f in fechas:
            for pan in tipo_pan:
                pan=data.loc[(data['Fecha'] == f) & (data['Pan'] == pan)].sum()
                cantidad_historico_panes.append(int(pan['Cantidad']))
                precio_historico_panes.append(float(pan['Precio']))
        
        #Inicializacion de arrays de cantidad y precio
        bolillos_can=[]
        muffins_can=[]
        donas_can=[]
        orejitas_can=[]
        conchas_can=[]
        
        bolillos_precio=[]
        muffins_precio=[]
        donas_precio=[]
        orejitas_precio=[]
        conchas_precio=[]
        
        for i in range(0,len(fechas)*len(tipo_pan),len(tipo_pan)):
            bolillos_can.append(cantidad_historico_panes[i])
            muffins_can.append(cantidad_historico_panes[i+1])
            donas_can.append(cantidad_historico_panes[i+2])
            orejitas_can.append(cantidad_historico_panes[i+3])
            conchas_can.append(cantidad_historico_panes[i+4])
            
            bolillos_precio.append(precio_historico_panes[i])
            muffins_precio.append(precio_historico_panes[i+1])
            donas_precio.append(precio_historico_panes[i+2])
            orejitas_precio.append(precio_historico_panes[i+3])
            conchas_precio.append(precio_historico_panes[i+4])
        
        plotear3datos(fechas,bolillos_can,conchas_can,orejitas_can,muffins_can,donas_can,'Cantidad',bucket)
        plotear3datos(fechas,bolillos_precio,conchas_precio,orejitas_precio,muffins_precio,donas_precio,'Venta',bucket)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Funciono :D')
    }
