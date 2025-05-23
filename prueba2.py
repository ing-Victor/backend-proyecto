import requests

# URL del endpoint
#url = "http://cc49-201-185-147-53.ngrok-free.app/login"
url = "https://indiecreator.net/work"

# Ciclo para enviar muchas solicitudes POST
for i in range(100000):
    data = {
        "dato": f"valor{i}"
    }

    try:
        #response = requests.post(url, data=data)
        response = requests.get(url, data=data)
        print(f"Petición {i+1}: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición {i+1}: {e}")

print("Prueba finalizada.")

