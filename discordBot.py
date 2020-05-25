from os import path
import json
import sqlite3

#import discord
from discord.ext.commands import Bot

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
            if valor > 0:
                print('[DISC] Actualizando {0} en la tabla PIZZAS en {1}'.format(usuario, self.rutaPizzas))   
                cursor.execute('''
                    UPDATE PIZZAS SET VALOR={1} WHERE ID={0}
                '''.format(usuario, valor))
            else:
                print('[DISC] Removiendo {0} de la tabla PIZZAS'.format(usuario, self.rutaPizzas))
                cursor.execute('''
                    DELETE FROM PIZZAS WHERE ID={0}
                '''.format(usuario))

        conexion.commit()
        conexion.close()

cliente = Bot(command_prefix='$')

@cliente.event
async def on_ready():
    print('[CLNT] Conectado exitosamente')

@cliente.command()
async def pizzas(contexto):
    dictPizzas = sorted(list(archivos.leerPizzas().items()), key=lambda x: x[1], reverse=True)

    if len(dictPizzas) > 0:
        for tupla in dictPizzas:
            usuario = cliente.get_user(tupla[0])
            valor = tupla[1]
            await contexto.send('{0}: {1}🍕'.format(usuario.mention, valor))
        totalPizzas = sum(map(lambda x: x[1], dictPizzas))
        await contexto.send('{0}🧑, {1}🍕, {2}🍕per🧑'.format(len(dictPizzas), totalPizzas, round(totalPizzas/len(dictPizzas), 2)))
    else:
        await contexto.send('Nadie debe pizzas')

@cliente.command()
async def añadirpizza(contexto):
    dictPizzas = archivos.leerPizzas()
    
    for persona in contexto.message.mentions:
        idUsuario = persona.id
        if idUsuario == 714300561465278525:
            await contexto.send('🤨')
            return
        
        if idUsuario not in dictPizzas:
            cantidad = 1
        else:
            cantidad = dictPizzas[idUsuario] + 1
        
        archivos.escribirPizzas(idUsuario, cantidad)
        await contexto.send('{0} ahora debe {1}🍕'.format(persona.mention, cantidad))

@cliente.command()
async def removerpizza(contexto):
    dictPizzas = archivos.leerPizzas()

    for persona in contexto.message.mentions:
        mensaje = '{0} no debe 🍕!'
        cantidad = 0
        
        idUsuario = persona.id
        if idUsuario == 714300561465278525:
            mensaje = '🤨'

        if idUsuario not in dictPizzas:
            pass
        else:
            if dictPizzas[idUsuario] == 0:
                pass
            else:
                mensaje = '{0} ahora debe {1}🍕'
                cantidad = dictPizzas[idUsuario] - 1
            archivos.escribirPizzas(idUsuario, cantidad)
        
            await contexto.send(mensaje.format(persona.mention, cantidad))

@cliente.command()
async def buenardo(contexto):
    await contexto.send('https://www.youtube.com/watch?v=3OGYzegOhF4')


archivos = manejoArchivos()
token = archivos.leerToken()
cliente.run(token)