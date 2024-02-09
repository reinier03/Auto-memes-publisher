import os
import requests
from bs4 import BeautifulSoup as bs
import telebot
import time
import threading
from flask import Flask, request
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup
import dill




user={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"}
bot=telebot.TeleBot(os.environ["token"])
diccionario={}


directorio_actual=os.path.dirname(os.path.abspath(__file__))
reima = 1413725506
limite=48
tiempo_espera=round(24*60/limite*60)
target=-1001161864648
restantes=1
hilo_publicaciones=False
hilo=""

bot.send_message(reima, "Estoy Online perra >:D")


if os.path.isfile(f"{directorio_actual}/variables"):
    with open(f"{directorio_actual}/variables", 'rb') as archivo:
        variables_cargadas = dill.load(archivo)
        for key, item in variables_cargadas:
            globals()[key]=[item]
            
            
def guardar_variables():
    with open(f"{directorio_actual}/variables", 'wb') as archivo:
        diccionario={
            "hilo_publicaciones": hilo_publicaciones
        }
        dill.dump(diccionario, archivo)
    return
    

bot.set_my_commands([
    telebot.types.BotCommand("start", "Muestra ayuda de este bot"),  
    telebot.types.BotCommand("mostrar", "Muestra el canal de destino y el tiempo de publicacion"),
    telebot.types.BotCommand("panel_administrador", "(admin) Solo disponible para mi creador ;)")    
])

def obtener_memes():
    global diccionario
    global user
    global limite
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
                
                
    return


def publicar(diccionario, user):
    global tiempo_espera
    global limite
    global restantes
    global target #reemplazar este valor con el chat id del destino
    for e, i in enumerate(diccionario, start=1):
        if hilo_publicaciones==False:
            return
        res=requests.get(diccionario[e][0], headers=user)
        
        with open(f"{os.path.basename(diccionario[e][0])}", "wb") as archivo_escritura:
            archivo_escritura.write(res.content)
            
        archivo_lectura=open(f"{os.path.basename(diccionario[e][0])}", "rb")
        try:
            if os.path.basename(diccionario[e][0]).split('.')[-1] == "jpeg":
                bot.send_photo(target, photo=archivo_lectura , caption=f"{diccionario[e][1]}\n\n@LastHopePosting", timeout=60)
                #bot.send_photo(target, photo=open(f"{os.path.basename(diccionario[e][0])}", "rb"), caption=f"{diccionario[e][1]}\n\n@LastHopePosting", timeout=60)
            else:
                bot.send_document(target, document=open(f"{os.path.basename(diccionario[e][0])}", "rb"), caption=f"{diccionario[e][1]}\n\n@LastHopePosting", timeout=60)
        except Exception as e:
            bot.send_message(reima, f"Ha ocurrido un error al mandar un archivo:\n\n{e}\n\nNombre del archivo: {os.path.basename(diccionario[e][0])}")
                    
        archivo_lectura.close()
        os.remove(os.path.basename(diccionario[e][0]))
        restantes=len(diccionario)-e
        print(f"Ya publiqué, procedo a dormir {time.strftime('%H:%M', time.localtime())}")
        time.sleep(tiempo_espera)
    return
            

def bucle_memes():
    while hilo_publicaciones:
        obtener_memes()
        publicar(diccionario, user)
    return bot.send_message(reima, "<u>ADVERTENCIA:</u>\nEl bucle de memes se ha detenido!", parse_mode="html", disable_notification=False)
    
              
#------------------------------COMANDOS PUBLICOS----------------------------------

@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(message.chat.id, """
                     Lo siento pero no estoy diseñado para ser usado :(
                     Solo puedes acceder a la informacion de la publicacion de memes en el/los canales en los que publico pero no puedes interactuar conmigo 
                     
                     /mostrar para ver la información
                     """)


@bot.message_handler(commands=["mostrar"])
def cmd_mostrar(message):
    global limite
    global target
    bot.send_message(message.chat.id, f"Actualmente mi canal de destino es @{bot.get_chat(target).username}\nEl limite de memes diarios es de {limite}\nLos publico cada {tiempo_espera//60} minutos\nY me faltan por publicar {restantes} memes")
    return 


#------------------------------COMANDOS PUBLICOS----------------------------------


@bot.message_handler(commands=["panel_administrador"])
def cmd_panel_admin(message):
    if not message.chat.id==reima:
        bot.send_message(message.chat.id, "No eres mi creador como para decirme qué hacer >:)")
    panel_control=InlineKeyboardMarkup(row_width=1)
    panel_control.add(InlineKeyboardButton("Crear hilo ✨", callback_data="comenzar"))
    panel_control.add(InlineKeyboardButton("Detener hilo 🖐", callback_data="detener"))
    panel_control.add(InlineKeyboardButton("Limite de memes 🛑", callback_data="limite"))
    panel_control.add(InlineKeyboardButton("Canal target 🎯", callback_data="target"))
    bot.send_message(reima, "Bienvenido Reima ;)\nEn que te puedo ayudar?", reply_markup=panel_control)
    

@bot.callback_query_handler(func=lambda x: True)
def cmd_recibir_query(call):
    global hilo
    if call.data=="comenzar":
        global hilo_publicaciones
        if hilo and not "stopped" in str(hilo):
            bot.send_message(reima, "Ya hay un hilo en ejecución!")
            return
        else:
            hilo_publicaciones=True
            guardar_variables()
            bot.send_message(reima, "Empezaré a publicar de inmediato :)")
            hilo=threading.Thread(name="hilo_memes", target=bucle_memes)
            hilo.start()
            return
        

    elif call.data=="detener":
        if hilo_publicaciones==False and not "stopped" in str(hilo):
            hilo_publicaciones=False
            bot.send_message(reima, "El hilo se va a detener en la proxima vuelta de bucle :v\n\nEspera hasta entonces")
            
            return
        elif hilo_publicaciones==False and "stopped" in str(hilo):
            bot.send_message(reima, "No hay ningún hilo en ejecución")
            return
        else:
            def detener():
                global hilo
                global hilo_publicaciones
                
                hilo_publicaciones=False
                bot.send_message(reima, "El hilo se va a detener en la proxima vuelta de bucle :v\n\nEspera hasta entonces")
                guardar_variables()
                return 
            detener()
        
        
        
    elif call.data=="limite":
        global limite
        global tiempo_espera
        msg=bot.send_message(reima, "Define un total de memes que se publicarán en el día\n\nYo me ocuparé de distriburlos equitativamente por cada hora", reply_markup=telebot.types.ForceReply())
        
        def registrar(message):
            global limite
            global tiempo_espera
            if not message.text.isdigit():
                msg=bot.send_message(reima, "Tiene que ser un valor numérico!")
                return bot.register_next_step_handler(msg, registrar)
            else:
                limite=int(message.text)
                tiempo_espera=round(24*60/limite*60)
                return bot.send_message(reima, f"Entendido!\n\nSe repartirán los {limite} memes cada {tiempo_espera//60} minutos :D")
        
        return bot.register_next_step_handler(msg, registrar)


        

    elif call.data=="target":
        def registrar_canal(message):
            global target
            global limite
            global tiempo_espera
            if not message.text.startswith("@"):
                canal=f"@{message.text}"
            else:
                canal=message.text
            try:    
                bot.get_chat(canal)
            except:
                bot.send_message(reima, "Ni siquiera estoy en el canal!, Úneme como admin y prueba de nuevo!")
                return
            if not bot.get_chat_member(canal, bot._user.id).status == 'administrator':
                bot.send_message(reima, "Ni siquiera Soy admin en el canal! Prueba de nuevo cuando lo sea!")
                return
            else:
                target=bot.get_chat(canal).id
                bot.send_message(reima, "Canal agregado exitosamente :)")
                return
            
        msg=bot.send_message(reima, f"Define el canal al que se le enviarán los memes, por defecto es @{bot.get_chat(target).username}\n\nPasame el @username del nuevo canal :)", reply_markup=telebot.types.ForceReply())
        bot.register_next_step_handler(msg, registrar_canal)


if hilo_publicaciones==True:
    bot.send_message(reima, "Al parecer me pausé pero ahora mismo recuperaré la publicación ;)")
    hilo=threading.Thread(name="hilo_memes", target=bucle_memes)
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
    
    
    

