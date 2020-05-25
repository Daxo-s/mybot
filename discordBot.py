from os import path
import json
import sqlite3

import discord
from discord.ext import commands

class manejoArchivos():
    rutaRaiz = path.dirname(__file__)
    rutaPizzas = path.join(rutaRaiz, 'pizzas.db')
    
    def leerToken(self):
        with open(path.join(self.rutaRaiz, 'config.json')) as archivo:
            config = json.load(archivo)
            archivo.close()
        
        token = config['token']
        return token
    
    def leerPizzas(self):
        conexion = sqlite3.connect(self.rutaPizzas)
        cursor = conexion.cursor()
        
        dictPizzas = {}
        
        try:
            cursor.execute('''
                CREATE TABLE PIZZAS(
                    ID INT PRIMARY KEY NOT NULL,
                    VALOR INT NOT NULL
                )
            ''')
            conexion.commit()
            print('[DISC] Tabla PIZZAS creada exitosamente')
        except:
            print('[DISC] Leyendo {0}'.format(self.rutaPizzas))
            cursor.execute('''
                SELECT ID, VALOR FROM PIZZAS
            ''')
            for pareja in cursor:
                dictPizzas[pareja[0]] = pareja[1]
        
        conexion.close()
        return dictPizzas
    
    def escribirPizzas(self, usuario, valor):
        conexion = sqlite3.connect(self.rutaPizzas)
        cursor = conexion.cursor()

        celda = cursor.execute('''
            SELECT 1 FROM PIZZAS WHERE ID={0}
        '''.format(usuario)).fetchone()
        if celda == None:
            print('[DISC] Añadiendo {0} a la tabla PIZZAS en {1}'.format(usuario, self.rutaPizzas))
            cursor.execute('''
                INSERT INTO PIZZAS(ID, VALOR)
                VALUES({0}, {1})    
            '''.format(usuario, valor))
        else:
            print('[DISC] Actualizando {0} en la tabla PIZZAS en {1}'.format(usuario, self.rutaPizzas))   
            cursor.execute('''
                UPDATE PIZZAS SET VALOR={1} WHERE ID={0}
            '''.format(usuario, valor))

        conexion.commit()
        conexion.close()

archivos = manejoArchivos()
cliente = commands.Bot(command_prefix='$')

@cliente.event
async def on_ready():
    print('[CLNT] Conectado exitosamente')


@cliente.command()
async def pizzas(contexto):
    pizzas = sorted(list(archivos.leerPizzas().items()), key=lambda x: x[1], reverse=True)

    if len(pizzas) > 0:
        for tupla in pizzas:
            mensaje = '{0} debe {1} pizza'
            if tupla[1] > 1:
                mensaje += 's'
            
            usuario = cliente.get_user(tupla[0])
            valor = tupla[1]
            await contexto.send(mensaje.format(usuario.mention, valor))
    else:
        await contexto.send('Nadie debe pizzas')

@cliente.command()
async def añadirpizza(contexto):
    pizzas = archivos.leerPizzas()
    
    for persona in contexto.message.mentions:
        idUsuario = persona.id
        
        mensaje = '{0} ahora debe {1} pizza'
        if idUsuario not in pizzas:
            cantidad = 1
        else:
            cantidad = pizzas[idUsuario] + 1
            mensaje += 's'
        
        archivos.escribirPizzas(idUsuario, cantidad)
        await contexto.send(mensaje.format(persona.mention, cantidad))

token = archivos.leerToken()
cliente.run(token)
#Arrancar el bot.