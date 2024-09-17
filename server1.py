from flask import Flask, request, jsonify
from thespian.actors import Actor, ActorSystem
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from datetime import datetime

app = Flask(__name__)
actor_system = ActorSystem('multiprocQueueBase')

# Actores
class ScraperActor(Actor):
    def receiveMessage(self, message, sender):
        url = message['url']
        filename = message['filename']
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Identificar el dominio de la URL
        domain = urlparse(url).netloc

        # Lógica de scraping según el dominio
        if 'mercadolibre.com' in domain:
            price = scrape_mercadolibre(soup)
        elif 'tiendamia.com' in domain:
            price = scrape_tiendamia(soup)
        elif 'fullh4rd.com' in domain:
            price = scrape_fullh4rd(soup)
        else:
            price = 'Dominio no soportado'

        if price != 'Dominio no soportado' and price != 'No encontrado':
            self.store_price(price, filename)
        self.send(sender, {'type': 'price_stored'})

    def store_price(self, price, filename):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a') as file:
            file.write(f"{now}, {price}\n")

class PriceReaderActor(Actor):
    def receiveMessage(self, message, sender):
        filename = message['filename']
        dates, prices = self.read_prices(filename)
        self.send(sender, {'type': 'prices_read', 'dates': dates, 'prices': prices})

    def read_prices(self, filename):
        if not os.path.exists(filename):
            return [], []
        dates = []
        prices = []
        with open(filename, 'r') as file:
            for line in file:
                try:
                    date_str, price_str = line.strip().split(', ')
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    price = float(price_str)
                    dates.append(date)
                    prices.append(price)
                except ValueError:
                    continue
        return dates, prices

# Funciones de scraping
def scrape_mercadolibre(soup):
    price_tag = soup.find('meta', {'itemprop': 'price'})
    return price_tag['content'] if price_tag else 'No encontrado'

def scrape_tiendamia(soup):
    price_tag = soup.find('span', class_='currency_price')
    if price_tag:
        price = price_tag.text.strip().replace('AR$', '').replace('.', '').replace(',', '.')
        return price
    return 'No encontrado'

def scrape_fullh4rd(soup):
    price_tag = soup.find('div', {'class': 'precio'})
    return price_tag.text.strip() if price_tag else 'No encontrado'

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data['url']
    filename = data['filename']
    actor_system.tell(scraper_actor, {'url': url, 'filename': filename})
    return jsonify({"status": "Scraping iniciado"}), 200

@app.route('/read_prices', methods=['GET'])
def read_prices():
    filename = request.args.get('filename')
    future = actor_system.ask(reader_actor, {'filename': filename}, 10)
    return jsonify(future), 200

@app.route('/plot_prices', methods=['POST'])
def plot_prices():
    data = request.json
    dates = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in data['dates']]
    prices = data['prices']
    filename = data['filename']
    plotter_actor = actor_system.createActor(PricePlotterActor)
    actor_system.tell(plotter_actor, {'dates': dates, 'prices': prices, 'filename': filename})
    return jsonify({"status": "Gráfico generado"}), 200

class PricePlotterActor(Actor):
    def receiveMessage(self, message, sender):
        dates = message['dates']
        prices = message['prices']
        filename = message['filename']
        self.plot_prices(dates, prices, filename)
        self.send(sender, {'type': 'prices_plotted'})

    def plot_prices(self, dates, prices, filename):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(dates, prices, marker='o', linestyle='-', color='b')
        plt.xlabel('Fecha')
        plt.ylabel('Precio')
        plt.title(f'Historial de Precios - {filename}')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{filename}_plot.png')
        plt.show()

if __name__ == "__main__":
    # Crear actores
    scraper_actor = actor_system.createActor(ScraperActor)
    reader_actor = actor_system.createActor(PriceReaderActor)
    app.run(host='0.0.0.0', port=5000)
