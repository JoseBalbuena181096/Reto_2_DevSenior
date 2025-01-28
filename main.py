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
                if  int(entrada) in list(range(1,7)):
                    return entrada
                print(f"Opción inválida. Válidas: {', '.join(list(range(1,7)))}")
            except Exception as e:
                print(f"Error {e}")

    def ejecutar(self):
        """Ejecución principal """
        while True:
            self.mostrar_menu()
            opcion = self.seleccionar_opcion()
            print(opcion)
            if opcion == "1":
                pass
            elif opcion == "6":
                print("Saliendo del sistema")
                sys.exit()

# ------- función principal y utilización -----------

def main():
    menu = Menu()
    menu.ejecutar()

if __name__ == "__main__":
   main()
