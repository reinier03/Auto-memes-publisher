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

reima = 1413725506
limite=72
tiempo_espera=(60//round(limite/24))*60
target=-1001161864648

bot.set_my_commands(
    telebot.types.BotCommand("limite", "Establece el limite diario de memes"),
    telebot.types.BotCommand("target", "Establece el canal de destino")
)

def obtener_memes():
    global diccionario
    global user
    contador=0
    diccionario.clear()
    while not len(diccionario)>=limite:
        contador+=1
        res=requests.get(f"https://es.memedroid.com/memes/random?page={contador}", headers=user)
        soup=bs(res.text, features="html.parser")
        articulos=soup.find_all("article", class_="gallery-item")
        for e, i in enumerate(articulos, start=len(diccionario)+1):
            try:
                imagen=i.find("img", class_="img-responsive grey-background").attrs.get("src")
                texto=i.find("a", class_="item-header-title dyn-link").text
                diccionario[e]=[imagen, texto]
                if len(diccionario)>= limite:
                    break
            except:
                video=i.find("video", class_="item-video gallery-item-video grey-background").find("source").attrs.get("src")
                texto=i.find("a", class_="item-header-title dyn-link").text
                diccionario[e]=[video, texto]
                if len(diccionario)>= limite:
                    break
                
                
    return publicar(diccionario, user)


def publicar(diccionario, user):
    global target #reemplazar este valor con el chat id del destino
    for e, i in enumerate(diccionario, start=1):
        res=requests.get(diccionario[e][0], headers=user)
        
        with open(f"{os.path.basename(diccionario[e][0])}", "wb") as archivo_escritura:
            archivo_escritura.write(res.content)
            
        archivo_lectura=open(f"{os.path.basename(diccionario[e][0])}", "rb")
        archivo_lectura.seek(0)
        if os.path.basename(diccionario[e][0]).split('.')[-1] == "jpeg":
            bot.send_photo(target, photo=archivo_lectura, caption=f"{diccionario[e][1]}\n\n@LastHopePosting")
        else:
            bot.send_document(target, document=archivo_lectura, caption=f"{diccionario[e][1]}\n\n@LastHopePosting", timeout=60)
                
        archivo_lectura.close()
        os.remove(os.path.basename(diccionario[e][0]))
        print(f"Ya publiqué, procedo a dormir {time.strftime('%H:%M', time.localtime())}")
        time.sleep(tiempo_espera)
    return obtener_memes()
            
                

if not threading.active_count() > 4:           
    hilo=threading.Thread(name="hilo", target=obtener_memes)
    hilo.start()




@bot.message_handler(commands=["limite"])
def cmd_limite(message):
    if not message.chat.id==reima:
        bot.send_message(reima, "No eres mi creador como para decirme qué hacer >:)")
        return
    msg=bot.send_message(reima, "Define un total de memes que se publicarán en el día\n\nYo me ocuparé de distriburlos equitativamente por cada hora", reply_markup=telebot.types.ForceReply())
    bot.register_next_step_handler(msg, registrar)

def registrar(message):
    global limite
    if not message.text.isdigit():
        msg=bot.send_message(reima, "Tiene que ser un valor numérico!")
        bot.register_next_step_handler(msg, registrar)
    else:
        limite=int(message.text)
        bot.send_message(reima, f"Entendido!n\n\nSe repartirán los {limite} memes cada {tiempo_espera*60} minutos :D")
        

@bot.message_handler(commands=["target"])
def cmd_canal_destino(message):
    if not message.chat.id==reima:
        bot.send_message(reima, "No eres mi creador como para decirme qué hacer >:)")
        return
    msg=bot.send_message(reima, f"Define el canal al que se le enviarán los memes, por defecto es {bot.get_chat(target)}\n\nPasame el @username del nuevo canal :)", reply_markup=telebot.types.ForceReply())
    bot.register_next_step_handler(msg, registrar_canal)

def registrar_canal(message):
    global target
    if not message.text.startswith("@"):
        canal=f"@{message.text}"
    else:
        canal=message.text
    try:    
        bot.get_chat(canal)
    except:
        bot.send_message(reima, "Ni siquiera estoy en el canal!, uneme como admin y prueba de nuevo!")
        return
    if not bot.get_chat_member(canal, bot._user.id).status == 'administrator':
        bot.send_message(reima, "Ni siquiera Soy admin en el canal! Prueba de nuevo cuando lo sea!")
        return
    else:
        target=canal
        bot.send_message(reima, "Canal agregado exitosamente :)")
        return

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
    
    
    

