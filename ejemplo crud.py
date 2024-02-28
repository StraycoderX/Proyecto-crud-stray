import http.server
import json
from urllib.parse import urlparse
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

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
            self.wfile.write(json.dumps(empleados).encode())
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

    # Función para manejar el inicio de sesión
    def iniciar_sesion():
        while True:
            usuario = simpledialog.askstring("Iniciar Sesión", "Usuario:")
            contraseña = simpledialog.askstring("Iniciar Sesión", "Contraseña:")
            if usuario == 'admin' and contraseña == 'Luca6grande':
                print("Inicio de sesión exitoso.")
                abrir_ventana_principal()
                break
            else:
                messagebox.showerror("Error", "Credenciales incorrectas. Inténtelo de nuevo.")

    # Función para abrir la ventana principal después de iniciar sesión
    def abrir_ventana_principal():
        root = tk.Tk()
        root.title("Gestión de Empleados")

        # Funciones para los botones
        def agregar_empleado():
            nombre = simpledialog.askstring("Agregar Empleado", "Nombre:")
            rol = simpledialog.askstring("Agregar Empleado", "Rol:")
            compania = simpledialog.askstring("Agregar Empleado", "Compañía:")
            nuevo_empleado = {'nombre': nombre, 'rol': rol, 'compania': compania}
            empleados.append(nuevo_empleado)
            guardar_empleados(empleados)
            messagebox.showinfo("Empleado Agregado", "Empleado agregado correctamente.")

        def modificar_empleado():
            indice = simpledialog.askinteger("Modificar Empleado", "Índice del empleado a modificar:")
            if indice is not None and 0 <= indice < len(empleados):
                nuevo_rol = simpledialog.askstring("Modificar Empleado", "Nuevo Rol:")
                empleados[indice]['rol'] = nuevo_rol
                guardar_empleados(empleados)
                messagebox.showinfo("Empleado Modificado", "Rol del empleado actualizado correctamente.")
            else:
                messagebox.showerror("Error", "Índice de empleado no válido.")

        def eliminar_empleado():
            indice = simpledialog.askinteger("Eliminar Empleado", "Índice del empleado a eliminar:")
            if indice is not None and 0 <= indice < len(empleados):
                del empleados[indice]
                guardar_empleados(empleados)
                messagebox.showinfo("Empleado Eliminado", "Empleado eliminado correctamente.")
            else:
                messagebox.showerror("Error", "Índice de empleado no válido.")

        def ver_empleados():
            ventana_empleados = tk.Toplevel(root)
            ventana_empleados.title("Lista de Empleados")
            txt_empleados = scrolledtext.ScrolledText(ventana_empleados, width=50, height=10)
            txt_empleados.pack(expand=True, fill='both')
            empleados_str = '\n'.join([f"Nombre: {empleado['nombre']}, Rol: {empleado['rol']}, Compañía: {empleado['compania']}" for empleado in empleados])
            txt_empleados.insert(tk.END, empleados_str)

        # Botones en la ventana principal
        btn_agregar = tk.Button(root, text="Agregar Empleado", command=agregar_empleado)
        btn_agregar.pack(pady=5)
        btn_modificar = tk.Button(root, text="Modificar Empleado", command=modificar_empleado)
        btn_modificar.pack(pady=5)
        btn_eliminar = tk.Button(root, text="Eliminar Empleado", command=eliminar_empleado)
        btn_eliminar.pack(pady=5)
        btn_ver = tk.Button(root, text="Ver Empleados", command=ver_empleados)
        btn_ver.pack(pady=5)

        root.mainloop()

    # Iniciar sesión al abrir el servidor
    iniciar_sesion()

    print("\nIniciando el servidor...")
    http.server.HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler).serve_forever()

if __name__ == '__main__':
    iniciar_servidor()
