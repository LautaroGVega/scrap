import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

async def fetch_product_data(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        soup = BeautifulSoup(await response.text(), 'html.parser')

        # Lógica para extraer el precio según la página
        if 'mercadolibre' in url:
            price_element = soup.find('span', class_='andes-money-amount__fraction')
            price = price_element.text.strip() if price_element else 'Precio no encontrado'
        elif 'venex' in url:
            price_element = soup.find('span', class_='price')
            price = price_element.text.strip() if price_element else 'Precio no encontrado'
        elif 'compragamer' in url:
            # Ejemplo de extracción más compleja para Compragamer
            # Ajustar según la estructura real de la página
            price_element = soup.find('div', class_='product-price')
            price = price_element.find('span').text.strip() if price_element else 'Precio no encontrado'
        else:
            price = 'Página no reconocida'

        return {'url': url, 'price': price}

async def main():
    urls = [
        'https://www.mercadolibre.com.ar/mouse-gamer-de-juego-hyperx-pulsefire-surge-hx-mc002b-negro/p/MLA10763791#polycard_client=search-nordic&searchVariation=MLA10763791&position=10&search_layout=stack&type=product&tracking_id=89e17dcc-54d3-4a6c-b760-1424841d184b&wid=MLA934640226&sid=search',
        'https://www.venex.com.ar/perifericos/mouse/mouse-logitech-m280-wireless-rojo.html?keywords=mouse',
        'https://compragamer.com/producto/Combo_Logitech_Teclado_Mouse_MK120_USB_4141?criterio=mouse'
    ]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch_product_data(session, url))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    # Crear un DataFrame de pandas para mejor visualización y análisis
    df = pd.DataFrame(results)
    print(df)

if __name__ == '__main__':
    asyncio.run(main())