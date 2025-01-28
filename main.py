"""
Sistema de gestión de la veterinaria con persistecia de datos a JSON
Para el reto de DevSenior code Python

Autor: José Ángel Balbuena Palma
Fecha: 27/01/2025
"""

from typing import List 
from enum import Enum
from datetime import datetime
import sys
from prettytable import PrettyTable

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

class Veterinario(Persona):
    def __init__(self, nombre: str, contacto: str, direccion: str, especialidad: str):
        super().__init__(nombre, contacto, direccion)
        self.especialidad = especialidad

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
    def __init__(self, mascota: 'Mascota', fecha: datetime, veterinario: Veterinario, servicio: Servicio):
        self.mascota = mascota
        self.fecha = fecha
        self.veterinario = veterinario
        self.servicio = servicio



# ------- Clase para la mascota --------------------
class Mascota:
    def __init__(self, nombre: str, especie: str, raza: str, edad: int, propietario: Cliente = None):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self. propietario = propietario
        self.historial: List[Cita] = [] 

    def agregar_cita(self, cita: Cita):
        self.historial.append(cita)

# ------- Menu y validación de datos ---------------

class Menu:
    def __init__(self):
        self.veterinaria = Veterinaria()
        self.opciones_validas = ["1", "2", "3", "4", "5", "6"]

    def mostrar_menu(self):
        """Mostrar las opciones del sistema """
        print("\n--- Menú Principal ---")
        print("1. Registrar Cliente")
        print("2. Registrar Mascota")
        print("3. Programar Cita")
        print("4. Consultar Historial de Mascota")
        print("5. Listar Todos los Clientes")
        print("6. Salir")

    def seleccionar_opcion(self):
        """ Gestiona la seleccion de opcion del usuario """
        while True:
            entrada = input("Seleccione una opción del menu: ").strip()
            try: # Verificar si es numerica
                if not entrada.isdigit():
                    raise Exception("La entrada no es un número válido.")
                if  entrada in self.opciones_validas:
                    return entrada
                print(f"Opción inválida. Válidas: {self.opciones_validas}")
            except Exception as e:
                print(f"Error {e}")

    def registrar_cliente(self):
        """ Registrar un cliente en el sistema """
        print("\n --- Registra un nuevo cliente ---")
        # Validar el nombre 
        while True:
            try:

                nombre = input("Nombre del ciente: ").strip()
                if not nombre:
                    raise ValueError("El nombre no puede estar vacío")
                if len(nombre) < 3:
                    raise ValueError('El nombre debe tener al menos 3 caracteres')
                break 
            except ValueError as e:
                print(f'El error fue {e}, intente de nuevo')

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

        nuevo_cliente = Cliente(nombre, contacto, direccion)
        self.veterinaria.clientes.append(nuevo_cliente)
        print(f'Cliente {nuevo_cliente.nombre} registrado exitosamente!')

    def registrar_mascota(self):
        """ Registrar una mascota en el sistema """
        print("\n --- Registra una nueva mascota ---")

        # Validaciones
        cliente = self.seleccionar_cliente()
        if not cliente:
            return 
            
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

        while True:
            try:
                edad = int(input("Ingrese la edad: ").strip())
                break
            except ValueError as e:
                print(f"El error es {e}")

        nueva_mascota = Mascota(nombre, especie, raza, edad, cliente)
        cliente.agregar_mascota(nueva_mascota)
        print(f'Mascota {nombre} registrada exitosamente! ')

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
        

    def ejecutar(self):
        """Ejecución principal """
        while True:
            self.mostrar_menu()
            opcion = self.seleccionar_opcion()
            print(opcion)
            if opcion == "1":
                self.registrar_cliente()
            if opcion == "2":
                self.registrar_mascota()
                
            elif opcion == "6":
                print("Saliendo del sistema")
                sys.exit()

# ------- función principal y utilización -----------

def main():
    menu = Menu()
    menu.ejecutar()

if __name__ == "__main__":
   main()
