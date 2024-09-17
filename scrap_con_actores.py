import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from thespian.actors import Actor, ActorSystem
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Función para extraer el precio de MercadoLibre
def scrape_mercadolibre(soup):
    price_tag = soup.find('meta', {'itemprop': 'price'})
    return price_tag['content'] if price_tag else 'No encontrado'

# Función actualizada para extraer el precio de Tiendamia
def scrape_tiendamia(soup):
    price_tag = soup.find('span', class_='currency_price')
    if price_tag:
        price = price_tag.text.strip().replace('AR$', '').replace('.', '').replace(',', '.')
        return price
    return 'No encontrado'

# Función para extraer el precio de FullH4rd
def scrape_fullh4rd(soup):
    price_tag = soup.find('div', {'class': 'precio'})
    return price_tag.text.strip() if price_tag else 'No encontrado'

# Actor para hacer scraping de una URL
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

# Actor para leer los precios almacenados
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

# Actor para graficar los precios
class PricePlotterActor(Actor):
    def receiveMessage(self, message, sender):
        dates = message['dates']
        prices = message['prices']
        filename = message['filename']
        self.plot_prices(dates, prices, filename)
        self.send(sender, {'type': 'prices_plotted'})

    def plot_prices(self, dates, prices, filename):
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

# Función principal para iniciar el sistema de actores
def main():
    # URLs y nombres de plataformas
    urls = {
        'MercadoLibre': 'https://www.mercadolibre.com.ar/auriculares-gamer-inalambricos-corsair-void-rgb-elite-wireless-carbon-con-luz-led/p/MLA15393127#polycard_client=search-nordic&searchVariation=MLA15393127&position=2&search_layout=stack&type=product&tracking_id=4974ffd3-7425-4f03-811e-9e33be6fab8f&wid=MLA1371746555&sid=search',
        'Tiendamia': 'https://tiendamia.com/ar/producto?amz=B07X8SJ8HM&pName=CORSAIR%20VOID%20RGB%20ELITE%20Wireless%20Gaming%20Headset%20&ndash;%207&period;1%20Surround%20Sound%20&ndash;%20Omni-Directional%20Microphone%20&ndash;%20Microfiber%20Mesh%20Earpads%20&ndash;%20Up%20to%2040ft%20Range%20&ndash;%20iCUE%20Compatible%20&ndash;%20PC&comma;%20Mac&comma;%20PS5&comma;%20PS4%20&ndash;%20Carbon'
    }
    
    filenames = {platform: f'precios{platform}.txt' for platform in urls}
    plot_filenames = {platform: f'graficos{platform}.png' for platform in urls}

    actor_system = ActorSystem('multiprocQueueBase')  # Crear el sistema de actores
    scraper_actors = {platform: actor_system.createActor(ScraperActor) for platform in urls}
    reader_actors = {platform: actor_system.createActor(PriceReaderActor) for platform in urls}
    plotter_actors = {platform: actor_system.createActor(PricePlotterActor) for platform in urls}

    # Enviar las URLs a los actores scraper
    for platform, url in urls.items():
        filename = filenames[platform]
        actor_system.tell(scraper_actors[platform], {'url': url, 'filename': filename})

    # Leer y graficar los precios para cada URL
    for platform in urls:
        filename = filenames[platform]
        plot_filename = plot_filenames[platform]
        future = actor_system.ask(reader_actors[platform], {'filename': filename}, 10)
        actor_system.tell(plotter_actors[platform], {'dates': future['dates'], 'prices': future['prices'], 'filename': plot_filename})

    print("Historiales y gráficos generados.")  # Mensaje final

    # Terminar el sistema de actores
    actor_system.shutdown()

if __name__ == "__main__":
    main()
