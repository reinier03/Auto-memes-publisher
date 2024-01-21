import discord
from flask import Flask, request
from threading import Thread

server_address="NO"

class EasyBot(discord.Client):
    __commands = []
    app = Flask('')

    @app.route('/')
    def home():
        global server_address
        server_address=request.host_url
        print(f"Hello, The bot is running on {request.host_url}")
        return "Hello, The bot is running"
    def runServer(self):
        self.app.run(host='0.0.0.0', port=8181)
    def keep_alive(self):
        t = Thread(target=self.runServer)
        t.start()
    async def on_ready(self):
        print("Bot acitvated! {0}".format(self.user))

    async def on_message(self, message):
        for command in self.__commands:
            if(message.content == command[0]):
                print("Channel: {0.channel} | User {0.author} : {0.content}".format(message))
                await message.channel.send(command[1])
    def setCommand(self, command, text):
        new_command = (command, text)
        self.__commands.append(new_command)
    def run(self, token):        
        self.keep_alive()
        return super().run(token)