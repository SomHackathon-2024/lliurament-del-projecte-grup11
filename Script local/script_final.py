#!/usr/bin/env python3
import subprocess
import json
import re
from pymongo import MongoClient
from datetime import datetime

# Ejecutar arp-scan y capturar la salida
result = subprocess.run(['sudo', 'arp-scan', '--localnet'], capture_output=True, text=True)
output = result.stdout

# Capturar la fecha y hora actual
fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Procesar la salida para obtener direcciones MAC
mac_addresses = []
for line in output.splitlines():
    if re.search(r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}', line):
        mac = line.split()[1]
        mac_addresses.append({"mac_address": mac, "timestamp": fecha})

# Guardar las direcciones MAC en un archivo JSON
ruta_archivo_json = '/home/kali/testio/testeo/final/gola.json'
with open(ruta_archivo_json, 'w') as file:
    json.dump(mac_addresses, file)

# Conexión a MongoDB
uri = "mongodb+srv://javiersernahuertas:ipyiGqZ1ZZEznP9n@cluster0.xgtnb0q.mongodb.net/"
client = MongoClient(uri)
db = client["macruter"]
collection = db["ruter01"]
mac_address = "88:f0:31:0f:af:81"

# Leer el archivo JSON
with open(ruta_archivo_json, 'r') as file:
    new_connections = json.load(file)

# Actualizar MongoDB
existing_router = collection.find_one({"mac_address": mac_address})
if existing_router:
    existing_connections = existing_router.get("connections", [])
    existing_connections.extend(new_connections)
    collection.update_one(
        {"mac_address": mac_address},
        {"$set": {"connections": existing_connections}}
    )
    print("Conexiones incorporadas al router existente.")
else:
    result = collection.insert_one({
        "mac_address": mac_address,
        "location": {"type": "Point", "coordinates": [-122.084, 37.422]},
        "connections": new_connections
    })
    print("Nuevo router insertado con las nuevas conexiones.")


