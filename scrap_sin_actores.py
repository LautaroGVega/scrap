import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Función para obtener el precio de la URL
def get_price(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    price_meta = soup.find('meta', itemprop='price')
    if price_meta:
        return float(price_meta['content'])
    return None

# Función para almacenar el precio y la fecha en un archivo
def store_price(price, filename='prices.txt'):
    with open(filename, 'a') as file:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{now}, {price}\n")

# Función para leer precios y fechas desde el archivo
def read_prices(filename='prices.txt'):
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

# Función para generar un gráfico
def plot_prices(dates, prices):
    plt.figure(figsize=(12, 6))
    plt.plot(dates, prices, marker='o', linestyle='-', color='b')
    plt.xlabel('Fecha')
    plt.ylabel('Precio')
    plt.title('Historial de Precios')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('prices_plot.png')
    plt.show()

def main():
    url = 'https://www.mercadolibre.com.ar/mouse-gamer-de-juego-logitechg-series-hero-g502-negro/p/MLA17485023'
    
    # Obtener el precio y almacenarlo
    price = get_price(url)
    if price is not None:
        store_price(price)
        print(f"Precio guardado: {price}")
    else:
        print("No se pudo obtener el precio.")

    # Leer precios y fechas, y graficar
    dates, prices = read_prices()
    if prices:
        plot_prices(dates, prices)
    else:
        print("No hay precios para graficar.")

if __name__ == "__main__":
    main()
