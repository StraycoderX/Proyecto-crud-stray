import http.server
import json
from urllib.parse import urlparse

# Nombre del archivo JSON donde se almacenará la información de los empleados
archivo_empleados = 'empleados.json'

# Función para cargar la lista de empleados desde el archivo JSON
def cargar_empleados():
    try:
        with open(archivo_empleados, 'r') as file:
            empleados = json.load(file)
    except FileNotFoundError:
        empleados = []
    return empleados

# Función para guardar la lista de empleados en el archivo JSON
def guardar_empleados(empleados):
    with open(archivo_empleados, 'w') as file:
        json.dump(empleados, file)

# Lista de empleados (simulación de una base de datos)
empleados = cargar_empleados()

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/empleados':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Agregar el identificador único a cada empleado en la lista
            empleados_con_id = [{'id': i, **empleado} for i, empleado in enumerate(empleados)]
            
            self.wfile.write(json.dumps(empleados_con_id).encode())
        elif path.startswith('/empleados/'):
            index = int(path.split('/')[2])
            if index >= 0 and index < len(empleados):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(empleados[index]).encode())
            else:
                self.send_error(404, 'Empleado no encontrado')
        else:
            self.send_error(404, 'Ruta no encontrada')

    def do_POST(self):
        if self.path == '/empleados':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            nuevo_empleado = json.loads(post_data.decode())
            # Agregar campos adicionales para el rol y la compañía
            nuevo_empleado['rol'] = 'empleado'
            nuevo_empleado['compania'] = 'atos' if nuevo_empleado.get('compania') == 'atos' else 'otra'
            empleados.append(nuevo_empleado)
            guardar_empleados(empleados)  # Guardar la lista actualizada
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Empleado agregado correctamente'}).encode())
        else:
            self.send_error(404, 'Ruta no encontrada')

    def do_PUT(self):
        if self.path.startswith('/empleados/'):
            index = int(self.path.split('/')[2])
            if 0 <= index < len(empleados):
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                nuevo_rol = json.loads(put_data.decode()).get('rol')
                if nuevo_rol:
                    empleados[index]['rol'] = nuevo_rol
                    guardar_empleados(empleados)  # Guardar la lista actualizada
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'message': 'Rol del empleado actualizado correctamente'}).encode())
                else:
                    self.send_error(400, 'Datos incompletos en la solicitud')
            else:
                self.send_error(404, 'Empleado no encontrado')
        else:
            self.send_error(404, 'Ruta no encontrada')

    def do_DELETE(self):
        if self.path.startswith('/empleados/'):
            index = int(self.path.split('/')[2])
            if 0 <= index < len(empleados):
                del empleados[index]
                guardar_empleados(empleados)  # Guardar la lista actualizada
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Empleado eliminado correctamente'}).encode())
            else:
                self.send_error(404, 'Empleado no encontrado')
        else:
            self.send_error(404, 'Ruta no encontrada')

# Función para iniciar el servidor con seguridad
def iniciar_servidor():
    print("Bienvenido al servidor de empleados")
    print("Por favor, inicie sesión para continuar.")
    while True:
        usuario = input("Usuario: ")
        contraseña = input("Contraseña: ")
        if usuario == 'admin' and contraseña == 'Luca6grande':
            print("Inicio de sesión exitoso.")
            break
        else:
            print("Credenciales incorrectas. Inténtelo de nuevo.")

    print("\nIniciando el servidor...")
    http.server.HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler).serve_forever()

if __name__ == '__main__':
    iniciar_servidor()
