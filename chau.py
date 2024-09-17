from thespian.actors import Actor, ActorSystem

class CompareActor(Actor):
    def receiveMessage(self, message, sender):
        prices = message
        valid_prices = [(source, price) for source, price in prices if price != 'No encontrado']
        if valid_prices:
            best_price = min(valid_prices, key=lambda x: float(x[1].replace(',', '').replace('.', '')))
            result = f"Mejor precio: {best_price[1]} en {best_price[0]}"
        else:
            result = "No se encontraron precios válidos."
        print(result)  # Imprime el resultado final

if __name__ == "__main__":
    actor_system = ActorSystem('multiprocTCPBase', {'Admin Port': 1900})  # Iniciar actor system con TCP
    actor_system.createActor(CompareActor)  # Crear CompareActor
