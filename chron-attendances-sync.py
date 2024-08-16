import os
import shutil
import json
import subprocess
import requests
import schedule
import time
from datetime import datetime
from getpass import getpass
from zk import ZK
import sys


CONFIG_FILE = os.path.join(os.getenv('APPDATA'), 'SyncBiometrics', 'config.json')
EXECUTABLE_DEST = os.path.join(os.getenv('APPDATA'), 'SyncBiometrics', 'chron-attendances-sync.exe')


BACKEND_URL = "http://localhost:3000/api/"


def autenticar():
    try:
        username = input("Username: ")
        password = getpass("Password: ")
        response = requests.post(f"{BACKEND_URL}auth", json={"username": username, "password": password})
        response.raise_for_status()
        empresa_id = response.json()['usuario']['empresa']
        token = response.json()['token']
        return token, empresa_id
    except requests.exceptions.RequestException as e:
        print(f"Error de autenticación: {e}")
        return None, None


def obtener_asistencias(ip, port):
    zk = ZK(ip, port=port, timeout=5)
    conn = None
    try:
        conn = zk.connect()
        attendances = conn.get_attendance()
        if attendances:
            attendances_format = [
                {
                    'deviceUserId': att.user_id,
                    'tiempoRegistro': att.timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                }
                for att in attendances
            ]
            conn.clear_attendance()
            return attendances_format
        else:
            print("No se encontraron asistencias.")
            return []
    except Exception as e:
        print(f"Error al obtener asistencias del dispositivo biométrico: {e}")
        return []
    finally:
        if conn:
            conn.disconnect()


def enviar_asistencias(asistencias, empresa_id, token):
    try:
        headers = {'x-token': token}
        response = requests.post(f"{BACKEND_URL}sync/sincronizar-asistencias/{empresa_id}", json={'asistencias': asistencias}, headers=headers)
        response.raise_for_status()
        print("Respuesta del backend:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar asistencias al backend: {e}")


def cargar_configuracion():
    try:
        print("Verificando existencia del archivo de configuración...")
        if os.path.exists(CONFIG_FILE):
            print(f"Archivo de configuración encontrado: {CONFIG_FILE}")
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print("Configuración cargada exitosamente.")
                return config
        else:
            print("Archivo de configuración no encontrado.")
        return None
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        return None


def guardar_configuracion(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print("Configuración guardada correctamente.")
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")


def tarea_programada():
    config = cargar_configuracion()
    if config:
        asistencias = obtener_asistencias(config['ip'], config['port'])
        if asistencias:
            enviar_asistencias(asistencias, config['empresa_id'], config['token'])
        else:
            print("No hay asistencias para sincronizar.")
    else:
        print("No se encontró la configuración. Asegúrate de haber configurado correctamente el sistema.")


def copiar_ejecutable():
    try:
        
        current_executable_path = sys.executable
        
        
        if not os.path.exists(EXECUTABLE_DEST):
            shutil.copy(current_executable_path, EXECUTABLE_DEST)
            print(f"Ejecutable copiado a {EXECUTABLE_DEST}")
    except Exception as e:
        print(f"Error al copiar el ejecutable: {e}")


def configurar_inicio_automatico():
    try:
        
        copiar_ejecutable()

        
        task_name = "SyncBiometrics"
        subprocess.run([
            'schtasks', '/create', '/f', '/tn', task_name,
            '/tr', EXECUTABLE_DEST, '/sc', 'onlogon', '/rl', 'highest'
        ], check=True)
        
        print("Configuración de inicio automático completada.")
    except Exception as e:
        print(f"Error al configurar el inicio automático: {e}")

def main():
    config = cargar_configuracion()

    if config:
        print("Cargando configuración existente...")
        token = config['token']
        empresa_id = config['empresa_id']
    else:
        ip = input("Ingrese la IP del dispositivo biométrico: ")
        port = int(input("Ingrese el puerto del dispositivo biométrico: "))

        token, empresa_id = autenticar()
        if not token:
            print("Falló la autenticación. No se realizará la instalación.")
            input("Presiona Enter para salir...")
            return

        
        config = {
            'ip': ip,
            'port': port,
            'backend_url': BACKEND_URL,
            'token': token,
            'empresa_id': empresa_id
        }
        guardar_configuracion(config)

        
        configurar_inicio_automatico()

    
    try:
        print("Programando la tarea diaria...")
        schedule.every().day.at("17:00").do(tarea_programada)
        print("Tarea programada exitosamente.")
    except Exception as e:
        print(f"Error al programar la tarea: {e}")
        input("Presiona Enter para salir...")
        return

    
    try:
        print("Iniciando bucle principal...")
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")

    input("Presiona Enter para salir...")

if __name__ == "__main__":  
    main()
