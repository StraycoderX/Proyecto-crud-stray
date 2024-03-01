import http.server
import json
from urllib.parse import urlparse
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import logging
import threading

# Configura il logger
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Nombre del archivo JSON donde se almacenará la información de los empleados
archivo_empleados = 'empleados.json'

def guardar_empleados(empleados):
    with open(archivo_empleados, 'w') as f:
        json.dump(empleados, f)

def cargar_empleados():
    try:
        with open(archivo_empleados, 'r') as f:
            empleados = json.load(f)
            # Aggiungere l'ID a ciascun impiegato durante il caricamento
            empleados_con_id = [{'id': i, **empleado} for i, empleado in enumerate(empleados)]
            return empleados_con_id
    except FileNotFoundError:
        return []

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
            if 0 <= index < len(empleados):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(empleados[index]).encode())
            else:
                self.send_error(404)

def iniciar_servidor():
    # Inizia il server
    http.server.HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler).serve_forever()

def iniciar_sesion():
    while True:
        usuario = simpledialog.askstring("Iniciar Sesión", "Usuario:")
        contraseña = simpledialog.askstring("Iniciar Sesión", "Contraseña:")
        if usuario == 'admin' and contraseña == 'Luca6grande':
            print("Inicio de sesión exitoso.")
            abrir_ventana_principal()
            break
        else:
            print("Credenciales incorrectas. Inténtelo de nuevo.")

def abrir_ventana_principal():
    root = tk.Tk()
    root.title("Gestión de Empleados")

    def on_closing():
        if messagebox.askokcancel("Cerrar", "¿Seguro que quieres cerrar esta ventana?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Funzioni per i bottoni
    def agregar_empleado():
        nombre = simpledialog.askstring("Agregar Empleado", "Nombre:")
        rol = simpledialog.askstring("Agregar Empleado", "Rol:")
        compania = simpledialog.askstring("Agregar Empleado", "Compañía:")
        nuevo_empleado = {'nombre': nombre, 'rol': rol, 'compania': compania}
        empleados.append(nuevo_empleado)
        guardar_empleados(empleados)
        messagebox.showinfo("Empleado Agregado", "Empleado agregado correctamente.")
        # Aggiungi un messaggio di log
        logger.info(f"Empleado agregado: {nuevo_empleado}")

    def modificar_empleado():
        indice = simpledialog.askinteger("Modificar Empleado", "Índice del empleado a modificar:")
        if indice is not None and 0 <= indice < len(empleados):
            nuevo_rol = simpledialog.askstring("Modificar Empleado", "Nuevo Rol:")
            empleado_modificado = empleados[indice].copy()
            empleado_modificado['rol'] = nuevo_rol
            empleados[indice] = empleado_modificado
            guardar_empleados(empleados)
            messagebox.showinfo("Empleado Modificado", "Rol del empleado actualizado correctamente.")
            # Aggiungi un messaggio di log
            logger.info(f"Empleado modificado en el índice {indice}: {empleado_modificado}")
        else:
            messagebox.showerror("Error", "Índice de empleado no válido.")

    def eliminar_empleado():
        indice = simpledialog.askinteger("Eliminar Empleado", "Índice del empleado a eliminar:")
        if indice is not None and 0 <= indice < len(empleados):
            empleado_eliminado = empleados.pop(indice)
            guardar_empleados(empleados)
            messagebox.showinfo("Empleado Eliminado", "Empleado eliminado correctamente.")
            # Aggiungi un messaggio di log
            logger.info(f"Empleado eliminado en el índice {indice}: {empleado_eliminado}")
        else:
            messagebox.showerror("Error", "Índice de empleado no válido.")

    def ver_empleados():
        ventana_empleados = tk.Toplevel(root)
        ventana_empleados.title("Lista de Empleados")
        txt_empleados = scrolledtext.ScrolledText(ventana_empleados, width=50, height=10)
        txt_empleados.pack(expand=True, fill='both')
        empleados_str = '\n'.join([f"ID: {empleado['id']}, Nombre: {empleado['nombre']}, Rol: {empleado['rol']}, Compañía: {empleado['compania']}" for empleado in empleados])
        txt_empleados.insert(tk.END, empleados_str)

    def ver_logs():
        ventana_logs = tk.Toplevel(root)
        ventana_logs.title("Logs del Servidor")
        txt_logs = scrolledtext.ScrolledText(ventana_logs, width=100, height=30)
        txt_logs.pack(expand=True, fill='both')

        # Carica i logs attuali nel widget di testo
        with open('server.log', 'r') as f:
            logs = f.read()
            txt_logs.insert(tk.END, logs)

        # Monitora i logs in tempo reale
        def monitorizar_log():
            with open('server.log', 'r') as f:
                while True:
                    line = f.readline()
                    if line:
                        txt_logs.insert(tk.END, line)
                        txt_logs.see(tk.END)
                    else:
                        time.sleep(0.1)
        # Avvia il monitoraggio dei log in un thread separato
        log_monitor_thread = threading.Thread(target=monitorizar_log)
        log_monitor_thread.start()

    # Botones en la ventana principal
    btn_agregar = tk.Button(root, text="Agregar Empleado", command=agregar_empleado)
    btn_agregar.pack(pady=5)
    btn_modificar = tk.Button(root, text="Modificar Empleado", command=modificar_empleado)
    btn_modificar.pack(pady=5)
    btn_eliminar = tk.Button(root, text="Eliminar Empleado", command=eliminar_empleado)
    btn_eliminar.pack(pady=5)
    btn_ver = tk.Button(root, text="Ver Empleados", command=ver_empleados)
    btn_ver.pack(pady=5)
    btn_logs = tk.Button(root, text="Ver Logs del Servidor", command=ver_logs)
    btn_logs.pack(pady=5)

    root.mainloop()

# Iniciar sesión al abrir el servidor
iniciar_sesion()

print("\nIniciando el servidor...")
# Avvia il server in un thread separato
server_thread = threading.Thread(target=iniciar_servidor)
server_thread.start()
