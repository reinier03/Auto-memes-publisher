import os
import requests
from bs4 import BeautifulSoup as bs
from time import sleep
import discord
import threading



intentos = discord.Intents.all()
client = discord.Client(intents=intentos)


user={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"}
diccionario={}


def obtener_memes():
    global diccionario
    global user
    contador=0
    diccionario.clear()
    while not len(diccionario)>=48:
        contador+=1
        res=requests.get(f"https://www.memedroid.com/memes/random?page={contador}", headers=user)
        soup=bs(res.text, features="html.parser")
        articulos=soup.find_all("article", class_="gallery-item")
        for e, i in enumerate(articulos, start=len(diccionario)+1):
            try:
                imagen=i.find("img", class_="img-responsive grey-background").attrs.get("src")
                texto=i.find("a", class_="item-header-title dyn-link").text
                diccionario[e]=[imagen, texto]
                if len(diccionario)>= 48:
                    break
            except:
                video=i.find("video", class_="item-video gallery-item-video grey-background").find("source").attrs.get("src")
                texto=i.find("a", class_="item-header-title dyn-link").text
                diccionario[e]=[video, texto]
                if len(diccionario)>= 48:
                    break
                
                
    return publicar(diccionario, user)


def publicar(diccionario, user):
    canal=client.get_channel(1189687855774191687) #reemplazar este valor con el chat id del destino
    for e, i in enumerate(diccionario, start=1):
        res=requests.get(diccionario[e][0], headers=user)
        
        with open(f"{os.path.basename(diccionario[e][0])}", "wb") as archivo_escritura:
            archivo_escritura.write(res.content)
            
        archivo_lectura=open(f"{os.path.basename(diccionario[e][0])}", "rb")
        archivo=discord.File(archivo_lectura)
        canal.send(f"{diccionario[e][1]}",file=archivo) 
                
        archivo_lectura.close()
        os.remove(os.path.basename(diccionario[e][0]))
        sleep(1800)
    return
            
                
@client.event
async def on_ready():
    while True:
        await obtener_memes()



client.run(os.environ["token"])
    
    

