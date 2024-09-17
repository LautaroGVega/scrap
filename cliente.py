import requests

def send_scraping_request(url, filename):
    response = requests.post('http://localhost:5000/scrape', json={'url': url, 'filename': filename})
    return response.json()

def read_prices(filename):
    response = requests.get(f'http://localhost:5000/read_prices?filename={filename}')
    return response.json()

def plot_prices(dates, prices, filename):
    response = requests.post('http://localhost:5000/plot_prices', json={'dates': dates, 'prices': prices, 'filename': filename})
    return response.json()

def main():
    urls = {
        'MercadoLibre': 'https://www.mercadolibre.com.ar/auriculares-gamer-inalambricos-corsair-void-rgb-elite-wireless-carbon-con-luz-led/p/MLA15393127#polycard_client=search-nordic&searchVariation=MLA15393127&position=2&search_layout=stack&type=product&tracking_id=4974ffd3-7425-4f03-811e-9e33be6fab8f&wid=MLA1371746555&sid=search',
        'Tiendamia': 'https://tiendamia.com/ar/producto?amz=B07X8SJ8HM&pName=CORSAIR%20VOID%20RGB%20ELITE%20Wireless%20Gaming%20Headset%20&ndash;%207&period;1%20Surround%20Sound%20&ndash;%20Omni-Directional%20Microphone%20&ndash;%20Microfiber%20Mesh%20Earpads%20&ndash;%20Up%20to%2040ft%20Range%20&ndash;%20iCUE%20Compatible%20&ndash;%20PC&comma;%20Mac&comma;%20PS5&comma;%20PS4%20&ndash;%20Carbon'
    }
    
    filenames = {platform: f'precios_{platform}.txt' for platform in urls}
    plot_filenames = {platform: f'graficos_{platform}.png' for platform in urls}

    # Enviar solicitudes de scraping
    for platform, url in urls.items():
        filename = filenames[platform]
        result = send_scraping_request(url, filename)
        print(f"Resultado del scraping para {platform}: {result}")

    # Leer precios y graficar para cada URL
    for platform in urls:
        filename = filenames[platform]
        prices_data = read_prices(filename)
        if prices_data['dates'] and prices_data['prices']:
            result = plot_prices(prices_data['dates'], prices_data['prices'], plot_filenames[platform])
            print(f"Resultado de la generación del gráfico para {platform}: {result}")
        else:
            print(f"No se encontraron datos para graficar para {platform}.")

if __name__ == "__main__":
    main()
