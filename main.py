"""
Sistema de gestión de la veterinaria con persistecia de datos a JSON
Para el reto de DevSenior code Python

Autor: José Ángel Balbuena Palma
Fecha: 27/01/2025
"""

from typing import List, Dict
from enum import Enum
from datetime import datetime
import json
import sys
from prettytable import PrettyTable

# ---------- Configuración persistencia --------------
ARCHIVO_DATOS = "datos_veterinaria.json"

# ---------- Clase para la veterinaria ---------------
class Veterinaria:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.clientes: List[Cliente] = []
            cls._instance.veterinarios: List[Veterinario] = []
            cls._instance.citas: List[Cita] = []
        return cls._instance

    def guardar_datos(self):
        """Serializa todos los datos a formato JSON y los guarda en archivo"""
        datos = {
            'clientes': [c.to_dict() for c in self.clientes],
            'veterinarios': [v.to_dict() for v in self.veterinarios],
            'citas': [c.to_dict() for c in self.citas]
        }
        with open(ARCHIVO_DATOS, 'w') as f:
            json.dump(datos, f, indent=2)

    def cargar_datos(self):
        """Carga los datos desde el archivo JSON y reconstruye los objetos"""
        try:
            with open(ARCHIVO_DATOS, 'r') as f:
                datos = json.load(f)
                
                # Reconstruir veterinarios
                self.veterinarios = [
                    Veterinario.from_dict(v) for v in datos.get('veterinarios', [])
                ]
                
                # Reconstruir clientes y mascotas
                self.clientes = [
                    Cliente.from_dict(c, self.veterinarios) for c in datos.get('clientes', [])
                ]
                
                # Reconstruir citas
                self.citas = [
                    Cita.from_dict(c, self.clientes, self.veterinarios) 
                    for c in datos.get('citas', [])
                ]
                
        except FileNotFoundError:
            print("No se encontró archivo de datos, iniciando con datos vacíos")
   
# ---------- Clase para la persona   ----------------
class Persona:
    def __init__(self, nombre: str, contacto: str, direccion: str):
        self._nombre = nombre
        self._contacto = contacto
        self._direccion = direccion

    @property
    def nombre(self):
        return self._nombre
    
    @property
    def contacto(self):
        return self._contacto
    
    @property
    def direccion(self):
        return self._direccion

    def to_dict(self):
        """ Serializr la persona a diccionario """
        return {
            'nombre': self._nombre,
            'contacto': self._contacto,
            'direccion': self._direccion
        }
    
# -------------- Herencias de la clase persona ----- 

# --------- Clase para un cliente ------------------

class Cliente(Persona):
    def __init__(self, nombre, contacto, direccion):
        super().__init__(nombre, contacto, direccion)
        self.mascotas: List[Mascota] = []
        
    def agregar_mascota(self, mascota):
        self.mascotas.append(mascota)

    def __str__(self):
        return f'Nombre: {self.nombre} - Direccion: {self.contacto}'

    @classmethod
    def from_dict(cls, datos: Dict, veterinarios: List):
        """Reconstruye un cliente desde diccionario"""
        cliente = cls(
            datos['nombre'],
            datos['contacto'],
            datos['direccion']
        )
        # Reconstruir mascotas
        cliente.mascotas = [
            Mascota.from_dict(m, veterinarios) 
            for m in datos.get('mascotas', [])
        ]
        # Asignar el propietario a cada mascota
        for mascota in cliente.mascotas:
            mascota.propietario = cliente
        return cliente

    def to_dict(self):
        """Serializa el cliente incluyendo sus mascotas"""
        datos = super().to_dict()
        datos['mascotas'] = [m.to_dict() for m in self.mascotas]
        return datos

# --------- Clase para un Veterinario ------------------
class Veterinario(Persona):
    def __init__(self, nombre: str, contacto: str, direccion: str, especialidad: str):
        super().__init__(nombre, contacto, direccion)
        self.especialidad = especialidad
    
    def __str__(self):
        return f'Nombre: {self.nombre} - especialidad {self.especialidad}'

    @classmethod
    def from_dict(cls, datos: Dict):
        return cls(
            datos['nombre'],
            datos['contacto'],
            datos['direccion'],
            datos['especialidad']
        )

    def to_dict(self):
        datos = super().to_dict()
        datos['especialidad'] = self.especialidad
        return datos  

# ------- Clases para el servicio y citas ----------

class Servicio(Enum):
    CONSULTA = "Consulta"
    VACUNACION = "Vacunación"
    CIRUGIA = "Cirugia"
    PELUCQUERIA = "Peluqueria"

    @classmethod
    def listar(cls):
        # retorna la lista se servicios
        return [s.value for s in cls]

class Cita:
    def __init__(self, mascota, fecha: datetime, veterinario: Veterinario, servicio: Servicio):
        self.mascota = mascota
        self.fecha = fecha
        self.veterinario = veterinario
        self.servicio = servicio

    def to_dict(self):
        """Serializa la cita a diccionario"""
        return {
            'mascota_nombre': self.mascota.nombre,
            'cliente_nombre': self.mascota.propietario.nombre,
            'fecha': self.fecha.strftime("%d/%m/%Y %H:%M"),
            'veterinario': self.veterinario.nombre,
            'servicio': self.servicio.value
        }

    @classmethod
    def from_dict(cls, datos: Dict, clientes: List[Cliente], veterinarios: List[Veterinario]):
        """Reconstruye una cita desde diccionario"""
        # Buscar mascota
        mascota = None
        for cliente in clientes:
            for m in cliente.mascotas:
                if m.nombre == datos['mascota_nombre'] and cliente.nombre == datos['cliente_nombre']:
                    mascota = m
                    break
            if mascota:
                break
                
        # Buscar veterinario
        veterinario = next((v for v in veterinarios if v.nombre == datos['veterinario']), None)
        fecha = datetime.strptime(datos['fecha'], "%d/%m/%Y %H:%M")
        servicio = Servicio(datos['servicio'])        
        return cls(mascota, fecha, veterinario, servicio)

# ------- Clase para la mascota --------------------
class Mascota:
    def __init__(self, nombre: str, especie: str, raza: str, edad: int, propietario: Cliente = None):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.propietario = propietario
        self.historial: List[Cita] = [] 

    def agregar_cita(self, cita: Cita):
        self.historial.append(cita)

    def __str__(self):
        return f'Nombre: {self.nombre} - Especie {self.especie} - Raza {self.raza}'

    @classmethod
    def from_dict(cls, datos: Dict, veterinarios: List[Veterinario]):
        """Reconstruye mascota desde diccionario"""
        mascota = cls(
            datos['nombre'],
            datos['especie'],
            datos['raza'],
            datos['edad']
        )
        # Reconstruir historial
        mascota.historial = [
            Cita.from_dict(c, [], veterinarios)  # Clientese cargan después
            for c in datos.get('historial', [])
        ]
        return mascota

    def to_dict(self):
        """Serializa la mascota incluyendo su historial"""
        return {
            'nombre': self.nombre,
            'especie': self.especie,
            'raza': self.raza,
            'edad': self.edad,
            'historial': [c.to_dict() for c in self.historial]
        }

# ------- Menu y validación de datos ---------------

class Menu:
    def __init__(self):
        self.veterinaria = Veterinaria()
        self.veterinaria.cargar_datos()
        self.opciones_validas = ["1", "2", "3", "4", "5", "6", "7"]

    def mostrar_menu(self):
        """Mostrar las opciones del sistema """
        print("\n--- Menú Principal ---")
        print("1. Registrar Cliente")
        print("2. Registrar Mascota")
        print("3. Programar Cita")
        print("4. Consultar Historial de Mascota")
        print("5. Listar Todos los Clientes")
        print("6. Registrar Veterinario")
        print("7. Salir")

    def seleccionar_opcion(self):
        """ Gestiona la seleccion de opcion del usuario """
        while True:
            entrada = input("Seleccione una opción del menu: ").strip()
            try: # Verificar si es numerica
                if not entrada.isdigit():
                    self.mostrar_menu()
                    raise Exception("La entrada no es un número válido.")
                if  entrada in self.opciones_validas:
                    return entrada
                print(f"Opción inválida. Válidas: {self.opciones_validas}")
            except Exception as e:
                print(f"Error {e}")

    # Métodos principales

    def registrar_cliente(self):
        """ Registrar un cliente en el sistema """
        print("\n --- Registra un nuevo cliente ---")
        # Validar el nombre 
        i = 0
        while True:
            try:
                nombre = input("Nombre del cliente: ").strip()
                if not nombre:
                    raise ValueError("El nombre no puede estar vacío")
                if len(nombre) < 3:
                    raise ValueError('El nombre debe tener al menos 3 caracteres')
                break 
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')

            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                contacto = input("Ingrese su contacto: ").strip()
                if not contacto:
                    raise ValueError('El contacto no puede estar vacío')
                if len(contacto) < 5:
                    raise ValueError('El contacto debe tener al menos 5 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')

            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                direccion = input("Ingrese su dirección: ").strip()
                if not direccion:
                    raise ValueError('La dirección no puede estar vacía')
                if len(direccion) < 5:
                    raise ValueError('La dirección debe tener al menos 5 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
           
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        nuevo_cliente = Cliente(nombre, contacto, direccion)
        self.veterinaria.clientes.append(nuevo_cliente)
        print(f'Cliente {nuevo_cliente.nombre} registrado exitosamente!')

    def registrar_veterinario(self):
        """ Registrar un veterinario en el sistema """
        print("\n --- Registra un nuevo veterinario ---")
        # Validar el nombre 
        i = 0
        while True:
            try:

                nombre = input("Nombre del veterinario: ").strip()
                if not nombre:
                    raise ValueError("El nombre no puede estar vacío")
                if len(nombre) < 3:
                    raise ValueError('El nombre debe tener al menos 3 caracteres')
                break 
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                contacto = input("Ingrese su contacto: ").strip()
                if not contacto:
                    raise ValueError('El contacto no puede estar vacío')
                if len(contacto) < 5:
                    raise ValueError('El contacto debe tener al menos 5 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                direccion = input("Ingrese su dirección: ").strip()
                if not direccion:
                    raise ValueError('La dirección no puede estar vacía')
                if len(direccion) < 5:
                    raise ValueError('La dirección debe tener al menos 5 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                especialidad = input("Ingrese su especialidad: ").strip()
                if not especialidad:
                    raise ValueError('La especialidad no puede estar vacía')
                if len(especialidad) < 5:
                    raise ValueError('La especialidad debe tener al menos 5 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        nuevo_veterinario = Veterinario(nombre, contacto, direccion, especialidad)
        self.veterinaria.veterinarios.append(nuevo_veterinario)
        print(f'Veterinario {nuevo_veterinario.nombre} {nuevo_veterinario.especialidad} registrado exitosamente!')

    def registrar_mascota(self):
        """ Registrar una mascota en el sistema """

        print("\n --- Registra una nueva mascota ---")
        # Validaciones
        cliente_mascota = self.seleccionar_cliente()
        if not cliente_mascota:
            return 
    
        i = 0    
        while True:
            try:
                nombre = input("Nombre de la mascota: ").strip()
                if not nombre:
                    raise ValueError("El nombre no puede estar vacío")
                if len(nombre) < 3:
                    raise ValueError('El nombre debe tener al menos 3 caracteres')
                break 
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return
        
        i = 0
        while True:
            try:
                especie = input("Ingrese su especie: ").strip()
                if not especie:
                    raise ValueError('La especie no puede estar vacía')
                if len(especie) < 3:
                    raise ValueError('La especie debe tener al menos 3 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i = 0
        while True:
            try:
                raza = input("Ingrese su raza: ").strip()
                if not raza:
                    raise ValueError('La raza no puede estar vacía')
                if len(raza) < 3:
                    raise ValueError('La raza debe tener al menos 3 caracteres')
                break
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        i  = 0
        while True:
            try:
                edad = int(input("Ingrese la edad: ").strip())
                break
            except ValueError as e:
                print(f"El error es {e}")
            i += 1
            if i>= 3:
                print("Demasiados intentos regresando... ")
                return

        nueva_mascota = Mascota(nombre, especie, raza, edad, cliente_mascota)
        cliente_mascota.agregar_mascota(nueva_mascota)
        print(f'Mascota {nombre} registrada exitosamente! ')

    def programar_cita(self):
        """ Programar una cita """
        print("\n---- Programar Nueva Cita ----")
        cliente = self.seleccionar_cliente()
        if not cliente:
            return
        
        mascota = self.seleccionar_mascota(cliente)
        if not mascota:
            return

        veterinario = self.seleccionar_veterinario()
        if not veterinario:
            return

        fecha_str = input("Feha y hora (DD/MM/AAAA HH:MM): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print('Formato de fecha inválido, Use DD/MM/AAAA HH:MM')
            return

        tabla = PrettyTable()
        # Definir columnas
        print("\nServicios disponibles: ")
        tabla.field_names = ["ID", "Nombre"]
        for id_, servicio in enumerate(Servicio.listar(), start=1):
            tabla.add_row([f'{id_}', f'{servicio}'])
            tabla.add_row([f' ',f' '])
        print(tabla)

        try:
            seleccion = int(input("Seleccione servicio: ")) - 1
            servicio = Servicio(Servicio.listar()[seleccion])
        except (ValueError, IndexError):
            print("Selección inválida")
            return

        nueva_cita = Cita(mascota, fecha, veterinario, servicio)
        mascota.agregar_cita(nueva_cita)
        print(mascota)
        self.veterinaria.citas.append(nueva_cita)
        print('Propietario : ', mascota.propietario.nombre)
        print(f'Cita programada para {mascota.nombre} el {fecha_str}')
                
    def consultar_historial(self):
        """ Muestra el historial médico de una mascota """
        print("\n---- Conusltar Historial ----")
        cliente = self.seleccionar_cliente()
        if not cliente:
            return
        
        mascota = self.seleccionar_mascota(cliente)
        if not mascota:
            return
        
        print(f'\n Historial de {mascota.nombre} ({mascota.especie})')
        if not mascota.historial:
            print("No hay citas registradas")
            return

        tabla = PrettyTable()
        tabla.field_names = ["Fecha", "Servicio", 'Veterinario', 'Especialidad']
        for id_, cita in enumerate(mascota.historial, start=1):
            tabla.add_row([
                f'{id_} - {cita.fecha.strftime('%d/%m/%Y %H:%M')}',
                f'{cita.servicio.value}',
                f'{cita.veterinario.nombre}',
                f'{cita.veterinario.especialidad}'
            ])
            tabla.add_row([f' ',f' ',f' ',f' '])
        print(tabla)        

    def listar_clientes(self):
        """ Muestra todos los clientes con sus mascotas """
        print("\n---- Listado de Clientes ----")
        if not self.veterinaria.clientes:
            print('No hay clientes que mostrar')
            return
        tabla = PrettyTable()
        # Definir columnas
        print("\nClientes disponibles:")
        tabla.field_names = ["ID", "Nombre", "Contacto", f"Mascotas"]
        for id_, cliente in enumerate(self.veterinaria.clientes, start=1):
            tabla.add_row([
                    f'{id_}', 
                    f'{cliente.nombre}',
                    f'{cliente.contacto}',
                    f'{"\n".join(map(lambda mascota: mascota.nombre, cliente.mascotas))}'
                ])
            tabla.add_row([f' ',f' ',f' ',f' '])
        print(tabla)


    # Métodos auxiliares 
    def seleccionar_cliente(self):
        """Mostrar la lista de clientes y permitir seleccionar uno """
        if not self.veterinaria.clientes:
            print('No tienes clientes')
            return None
        tabla = PrettyTable()
        # Definir columnas
        print("\nClientes disponibles:")
        tabla.field_names = ["ID", "Nombre"]
        for id_, cliente in enumerate(self.veterinaria.clientes, start=1):
            tabla.add_row([f'{id_}', f'{cliente.nombre}'])
            tabla.add_row([f' ',f' '])
        print(tabla)

        try:
            seleccion = int(input("Seleccione un cliente: ")) - 1
            if seleccion >= 0 and seleccion < len(self.veterinaria.clientes):
                return self.veterinaria.clientes[seleccion]
            raise ValueError('Ingrese un cliente valido')
        except (ValueError, IndexError) as e:
            print(f"Selección inválida: {e}")
            return None
        
    def seleccionar_mascota(self, cliente:Cliente):
        """ Muestra mascotas de un cliente y permite seleccionar una """
        if not cliente.mascotas:
            print("Este cliente no tiene mascotas")
            return None
        tabla = PrettyTable()
        # Definir columnas
        print(f"\nMascotas de {cliente.nombre}: ")
        tabla.field_names = ["ID", "Nombre", f'Especie']
        for id_, mascota in enumerate(cliente.mascotas, start=1):
            tabla.add_row([f'{id_}', f'{mascota.nombre}', f'{mascota.especie}'])
            tabla.add_row([f' ',f' ',f' '])
        print(tabla)

        try:
            seleccion = int(input("Seleccione una mascota: ")) - 1
            if seleccion >= 0 and seleccion < len(cliente.mascotas):
                return cliente.mascotas[seleccion]
            raise ValueError('Ingrese una mascota valida')
        except (ValueError, IndexError) as e:
            print(f"Selección inválida: {e}")
            return None

    def seleccionar_veterinario(self):
        """Mostrar la lista de veterinarios y permitir seleccionar uno """
        if not self.veterinaria.veterinarios:
            print('No tienes veterinarios')
            return None
        tabla = PrettyTable()
        # Definir columnas
        print("\nVeterinarios disponibles:")
        tabla.field_names = ["ID", "Nombre", "Especialidad"]
        for id_, veterinario in enumerate(self.veterinaria.veterinarios, start=1):
            tabla.add_row([f'{id_}', f'{veterinario.nombre}', f'{veterinario.especialidad}'])
            tabla.add_row([f' ',f' ', f' '])
        print(tabla)

        try:
            seleccion = int(input("Seleccione un veterinario: ")) - 1
            if seleccion >= 0 and seleccion < len(self.veterinaria.veterinarios):
                return self.veterinaria.veterinarios[seleccion]
            raise ValueError('Ingrese un veterinario valido')
        except (ValueError, IndexError) as e:
            print(f"Selección inválida: {e}")
            return None

    def ejecutar(self):
        """Ejecución principal """
        while True:
            self.mostrar_menu()
            opcion = self.seleccionar_opcion()
            print(opcion)
            if opcion == "1":
                self.registrar_cliente()
            elif opcion == "2":
                self.registrar_mascota()
            elif opcion == "3":
                self.programar_cita()
            elif opcion == "4":
                self.consultar_historial()
            elif opcion == "5":
                self.listar_clientes()
            elif opcion == "6":
                self.registrar_veterinario()    
            elif opcion == "7":
                self.veterinaria.guardar_datos()
                print("Saliendo del sistema")
                sys.exit()

# ------- función principal y utilización -----------

def main():
    menu = Menu()
    menu.ejecutar()

if __name__ == "__main__":
   main()
