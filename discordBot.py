from os import path
import json
import sqlite3

import asyncio

import discord
from discord.ext.commands import Bot

class ManejoArchivos():
    rutaRaiz = path.dirname(__file__)
    rutaPizzas = path.join(rutaRaiz, 'pizzas.db')
    
    def leerToken(self):
        with open(path.join(self.rutaRaiz, 'config.json')) as archivo:
            config = json.load(archivo)
            archivo.close()
        
        token = config['token']
        return token
    
    '''
    def leerEmijiOpciones(self):
        with open(path.join(self.rutaRaiz, 'config.json')) as archivo:
            config = json.load(archivo)
            archivo.close()
        
        opciones = {
            'si': config['emojiSi'],
            'no': config['emojiNo']
        }
        return opciones
    '''
    
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


idBot = 714300561465278525
opciones = {
    'si': '\N{REGIONAL INDICATOR SYMBOL LETTER S}',
    'no': '\N{REGIONAL INDICATOR SYMBOL LETTER N}'
}
tiempoOpciones = 300
cliente = Bot(command_prefix='$')

@cliente.event
async def on_ready():
    print('[CLNT] Conectado exitosamente')

'''
@cliente.event
async def on_reaction_add(reaccion, usuario):
    if reaccion.message.author.id != idBot:
        return
    
    print('[LOG ] {0}'.format(reaccion.emoji.encode('ascii', 'namereplace')))
'''

@cliente.command()
async def pizzas(contexto):
    dictPizzas = sorted(list(archivos.leerPizzas().items()), key=lambda x: x[1], reverse=True)

    if len(dictPizzas) > 0:
        mensaje = ''
        for tupla in dictPizzas:
            usuario = cliente.get_user(tupla[0])
            valor = tupla[1]
            mensaje += '{0}: {1}🍕\n'.format(usuario.mention, valor)
        totalPizzas = sum(map(lambda x: x[1], dictPizzas))
        mensaje += '{0}🧑, {1}🍕, {2}🍕per🧑'.format(len(dictPizzas), totalPizzas, round(totalPizzas/len(dictPizzas), 2))
    else:
        mensaje = 'Nadie debe pizzas'
    await contexto.send(mensaje)

@cliente.command()
async def añadirpizza(contexto):
    dictPizzas = archivos.leerPizzas()
    
    for destino in contexto.message.mentions:
        idUsuario = destino.id
        if idUsuario == idBot:
            await contexto.send('🤨')
            return
        
        if idUsuario not in dictPizzas:
            cantidad = 1
        else:
            cantidad = dictPizzas[idUsuario] + 1
        miMensaje = await contexto.send('{0}, ¿Confirmas?'.format(destino.mention))
        await miMensaje.add_reaction(opciones['si']),
        await miMensaje.add_reaction(opciones['no'])

        reaccion = None
        try:
            reaccion, emisor = await cliente.wait_for('reaction_add', check=lambda reaction, user: user == destino, timeout=tiempoOpciones)
        except asyncio.TimeoutError:
            await miMensaje.delete()
            await contexto.send(content='Lo siento {0}, parece que esta vez no habrá pizza 😥'.format(contexto.author.mention))

        if reaccion != None and reaccion.message.id == miMensaje.id and reaccion.emoji == opciones['si']:
            archivos.escribirPizzas(idUsuario, cantidad)
            await miMensaje.remove_reaction(opciones['si'])
            await miMensaje.remove_reaction(opciones['no'])

            await contexto.send('{0} ahora debe {1}🍕'.format(destino.mention, cantidad))

@cliente.command()
async def removerpizza(contexto):
    dictPizzas = archivos.leerPizzas()

    for persona in contexto.message.mentions:
        mensaje = '{0} no debe 🍕!'
        cantidad = 0
        
        idUsuario = persona.id
        if idUsuario == idBot:
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


archivos = ManejoArchivos()
token = archivos.leerToken()
cliente.run(token)