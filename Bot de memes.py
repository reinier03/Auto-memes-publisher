import os
import requests
from bs4 import BeautifulSoup as bs
import telebot
from time import sleep


user={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"}
bot=telebot.TeleBot(os.environ["token"])
diccionario={}


def obtener_memes():
    global diccionario
    global user
    contador=0
    diccionario.clear()
    while not len(diccionario)>=48:
        contador+=1
        res=requests.get(f"https://es.memedroid.com/memes/random?page={contador}", headers=user)
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
    target=-1001161864648 #reemplazar este valor con el chat id del destino
    for e, i in enumerate(diccionario, start=1):
        res=requests.get(diccionario[e][0], headers=user)
        
        with open(f"{os.path.basename(diccionario[e][0])}", "wb") as archivo_escritura:
            archivo_escritura.write(res.content)
            
        archivo_lectura=open(f"{os.path.basename(diccionario[e][0])}", "rb")
        archivo_lectura.seek(0)
        if os.path.basename(diccionario[e][0]).split('.')[-1] == "jpeg":
            bot.send_photo(-1001161864648, photo=archivo_lectura, caption=f"{diccionario[e][1]}\n\n@LastHopePosting")
        else:
            bot.send_document(-1001161864648, document=archivo_lectura, caption=f"{diccionario[e][1]}\n\n@LastHopePosting", timeout=60)
                
        archivo_lectura.close()
        os.remove(os.path.basename(diccionario[e][0]))
        sleep(1800)
    return
            
                
                
                
obtener_memes()

bot.polling()
    
    
    

