# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hola desde el servidor"

@app.route('/mensaje', methods=['POST'])
def recibir_mensaje():
    data = request.json
    
    # Registra el mensaje recibido en la consola del servidor
    print(f"Mensaje recibido del cliente: {data}")
    
    return jsonify({"received": data}), 200

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
