import discord
from discord.ext import commands

cliente = commands.Bot(command_prefix='$')

@cliente.event
async def on_ready():
    print('Conectado exitosamente')

listaPizzas = {}
@cliente.command()
async def pizzas(contexto):
    pizzas = sorted(list(listaPizzas.items()), key=lambda x: x[1], reverse=True)
    print(pizzas)

    if len(listaPizzas) > 0:
        for tupla in pizzas:
            if tupla[1] > 1:
                await contexto.send('{0} debe {1} pizzas.'.format(tupla[0].mention, tupla[1]))
            else:
                await contexto.send('{0} debe {1} pizza.'.format(tupla[0].mention, tupla[1]))
    else:
        await contexto.send('Nadie debe pizzas.')

@cliente.command()
async def añadirpizza(contexto):
    for persona in contexto.message.mentions:
        if persona not in listaPizzas:
            listaPizzas[persona] = 0
        listaPizzas[persona] += 1
        
        if listaPizzas[persona] > 1:
            await contexto.send('{0} ahora debe {1} pizzas.'.format(persona.mention, listaPizzas[persona]))
        else:
            await contexto.send('{0} ahora debe {1} pizza.'.format(persona.mention, listaPizzas[persona]))


cliente.run('NzE0MzAwNTYxNDY1Mjc4NTI1.Xss22w.SaqMJ0t8n0e0dqvpGeKssIc4lpU')