import requests
from bs4 import BeautifulSoup
from thespian.actors import Actor, ActorSystem

# Actor para hacer scraping de una URL
class ScraperActor(Actor):
    def receiveMessage(self, message, sender):
        url = message
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Buscar el precio dentro de la etiqueta meta
        price_tag = soup.find('meta', {'itemprop': 'price'})
        if price_tag:
            price = price_tag['content']
        else:
            price = 'No encontrado'
        self.send(sender, (url, price))

# Actor para comparar precios
class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price) for source, price in prices if price != 'No encontrado']
        
        if valid_prices:
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            result = f"Mejor precio: {best_price[1]} en {best_price[0]}"
        else:
            result = "No se encontraron precios válidos."
        
        self.send(sender, result)

# URLs proporcionadas
urls = [
    'https://www.mercadolibre.com.ar/mouse-gamer-de-juego-hyperx-pulsefire-surge-hx-mc002b-negro/p/MLA10763791#polycard_client=search-nordic&searchVariation=MLA10763791&position=10&search_layout=stack&type=product&tracking_id=89e17dcc-54d3-4a6c-b760-1424841d184b&wid=MLA934640226&sid=search',
    'https://www.mercadolibre.com.ar/mouse-gamer-de-juego-logitechg-series-hero-g502-negro/p/MLA17485023#polycard_client=search-nordic&searchVariation=MLA17485023&position=1&search_layout=stack&type=product&tracking_id=6203f7d6-a8bb-4c17-a5c9-2cfe36f2ad44&wid=MLA1730800598&sid=search',
    'https://www.mercadolibre.com.ar/logitech-g-serie-g-lightspeed-g305-black/p/MLA11259955#polycard_client=search-nordic&searchVariation=MLA11259955&position=1&search_layout=stack&type=product&tracking_id=b6cb51ba-6e33-400c-ab0c-c82d14ae7ad7&wid=MLA1369467985&sid=search'
]

# Función principal para iniciar el sistema de actores
def main():
    actor_system = ActorSystem()  # Crear el sistema de actores
    scraper_actors = [actor_system.createActor(ScraperActor) for _ in urls]
    compare_actor = actor_system.createActor(CompareActor)
    
    # Enviar las URLs a los actores scraper
    future = actor_system.ask(compare_actor, [(actor_system.ask(scraper, url, 10)) for scraper, url in zip(scraper_actors, urls)], 10)
    
    # Imprimir el resultado final
    print(future)
    
    # Terminar el sistema de actores
    actor_system.shutdown()

if __name__ == "__main__":
    main()
