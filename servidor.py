from thespian.actors import ActorSystem, Actor, ActorTypeDispatcher
import json
from flask import Flask, request

app = Flask(__name__)

# Definición del actor
class EchoActor(Actor):
    def receiveMessage(self, message, sender):
        print(f"Received message: {message}")
        self.send(sender, f"Echo: {message}")

# Configuración del sistema de actores
system = ActorSystem('multiprocTCPBase')

# Crear y registrar el actor
echo_actor = system.createActor(EchoActor)

# Endpoint para recibir mensajes del cliente
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    response = system.ask(echo_actor, message)
    return json.dumps({'response': response}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
