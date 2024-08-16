import requests
from getpass import getpass
from zk import ZK, const

def autenticar():
    username = input("Username: ")
    password = getpass("Password: ")
    try:
        response = requests.post("http://localhost:3000/api/auth", json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        empresa_id = response.json()['usuario']['empresa']
        return response.json(), empresa_id
    except requests.exceptions.RequestException as error:
        print(f"Error de autenticación: {error}")
        return None, None

def sincronizar_usuarios_biometricos(url, token, dispositivo_ip, dispositivo_puerto, empresa_id):
    zk = ZK(dispositivo_ip, port=int(dispositivo_puerto), timeout=5)
    conn = None
    try:
        print('Connecting to device ...')
        conn = zk.connect()
        print('Disabling device ...')
        conn.disable_device()

        print('Fetching users from biometric device...')
        biometric_users = conn.get_users()

        response = requests.get(f"{url}/api/empleados/company/all/{empresa_id}", headers={'x-token': token})
        response.raise_for_status()
        db_users = response.json()['empleados']

        db_users_map = {str(user['uidBiometrico']): user for user in db_users}

        new_users = [user for user in biometric_users if str(user.uid) not in db_users_map]

        for new_user in new_users:
            requests.post(f"{url}/api/empleados", json={
                "uidBiometrico": new_user.uid,
                "nombre": new_user.name,
                "empresa": empresa_id
            }, headers={'x-token': token})

        print(f"Sincronización completada. {len(new_users)} usuarios nuevos creados.")

        print('Enabling device...')
        conn.enable_device()
    except Exception as e:
        print(f"Process terminated: {e}")
    finally:
        if conn:
            conn.disconnect()

def main():
    dispositivo_ip = input("Ingrese la IP del dispositivo biométrico: ")
    dispositivo_puerto = input("Ingrese el puerto del dispositivo biométrico: ")

    token, empresa_id = autenticar()
    if token:
        print("Autenticación exitosa")
        sincronizar_usuarios_biometricos('http://localhost:3000', token['token'], dispositivo_ip, dispositivo_puerto, empresa_id)
    else:
        print("Falló la autenticación")

    # Pausa al final para evitar que el script se cierre inmediatamente
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
