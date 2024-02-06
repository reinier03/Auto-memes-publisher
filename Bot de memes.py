import os
import requests
from bs4 import BeautifulSoup as bs
import telebot
import time
import threading
from flask import Flask, request


user={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"}
bot=telebot.TeleBot(os.environ['token'])
diccionario={}



def obtener_memes():
    global diccionario
    global user
    contador=0
    diccionario.clear()
    while not len(diccionario)>=72:
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
        print(f"Ya publiqué, procedo a dormir {time.strftime('%H:%M', time.localtime())}")
        time.sleep(1200)
    return obtener_memes()
            
                

if not threading.active_count() > 4:           
    hilo=threading.Thread(name="hilo", target=obtener_memes)
    hilo.start()




app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    host_url = request.host_url
    return f'¡Hola! Esta es la dirección local del host: {host_url}'

def flask():
    bot.remove_webhook()
    time.sleep(1)
    app.run(host="0.0.0.0", port=5000)


for i in threading.enumerate():
    if "hilo_flask" in str(i):
        break
else:
    hilo_flask=threading.Thread(name="hilo_flask", target=flask)
    hilo_flask.start()

bot.polling()
    
    
    

