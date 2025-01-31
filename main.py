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
        try:
            datos = {
                'veterinarios': [],
                'clientes': [],
                'citas': []
            }
            
            # Guardar veterinarios
            for veterinario in self.veterinarios:
                try:
                    if veterinario is not None:
                        datos['veterinarios'].append(veterinario.to_dict())
                except Exception as e:
                    print(f"Error al serializar veterinario: {e}")
            
            # Guardar clientes y sus mascotas
            for cliente in self.clientes:
                try:
                    if cliente is not None:
                        datos['clientes'].append(cliente.to_dict())
                except Exception as e:
                    print(f"Error al serializar cliente: {e}")
            
            # Guardar citas
            for cita in self.citas:
                try:
                    if cita is not None:
                        datos['citas'].append(cita.to_dict())
                except Exception as e:
                    print(f"Error al serializar cita: {e}")
            
            # Crear backup del archivo existente si existe
            try:
                import os
                if os.path.exists(ARCHIVO_DATOS):
                    import shutil
                    backup_file = f"{ARCHIVO_DATOS}.backup"
                    shutil.copy2(ARCHIVO_DATOS, backup_file)
            except Exception as e:
                print(f"No se pudo crear backup: {e}")
            
            # Guardar los datos en el archivo
            with open(ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
                
            print("Datos guardados exitosamente")
            
        except Exception as e:
            print(f"Error al guardar los datos: {e}")
            raise

    def cargar_datos(self):
        """Carga los datos desde el archivo JSON y reconstruye los objetos"""
        try:
            with open(ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
                # Limpiar las listas actuales
                self.veterinarios.clear()
                self.clientes.clear()
                self.citas.clear()
                
                # Primero cargar veterinarios
                for vet_data in datos.get('veterinarios', []):
                    try:
                        veterinario = Veterinario.from_dict(vet_data)
                        self.veterinarios.append(veterinario)
                    except Exception as e:
                        print(f"Error al cargar veterinario: {e}")
                
                # Luego cargar clientes y mascotas
                for cliente_data in datos.get('clientes', []):
                    try:
                        cliente = Cliente.from_dict(cliente_data, self.veterinarios)
                        self.clientes.append(cliente)
                    except Exception as e:
                        print(f"Error al cargar cliente: {e}")
                
                # Finalmente cargar citas
                for cita_data in datos.get('citas', []):
                    try:
                        # Encontrar mascota y cliente
                        mascota = None
                        for cliente in self.clientes:
                            for m in cliente.mascotas:
                                if (m.nombre == cita_data['mascota_nombre'] and 
                                    cliente.nombre == cita_data['cliente_nombre']):
                                    mascota = m
                                    break
                            if mascota:
                                break
                                
                        if not mascota:
                            print(f"No se encontró la mascota {cita_data['mascota_nombre']}")
                            continue
                            
                        # Encontrar veterinario
                        veterinario = next(
                            (v for v in self.veterinarios if v.nombre == cita_data['veterinario']),
                            None
                        )
                        if not veterinario:
                            print(f"No se encontró el veterinario {cita_data['veterinario']}")
                            continue
                            
                        fecha = datetime.strptime(cita_data['fecha'], "%d/%m/%Y %H:%M")
                        servicio = Servicio(cita_data['servicio'])
                        
                        cita = Cita(mascota, fecha, veterinario, servicio)
                        mascota.agregar_cita(cita)
                        self.citas.append(cita)
                        
                    except Exception as e:
                        print(f"Error al cargar cita: {e}")
                        
        except FileNotFoundError:
            print("No se encontró archivo de datos, iniciando con datos vacíos")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el archivo JSON: {e}")
        except Exception as e:
            print(f"Error inesperado al cargar datos: {e}")

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
        # Llamar correctamente al constructor de la clase padre
        Persona.__init__(self, nombre, contacto, direccion)
        # Inicializar la lista de mascotas
        self.mascotas: List[Mascota] = []

    def agregar_mascota(self, mascota):
        """Agrega una mascota a la lista del cliente"""
        if mascota not in self.mascotas:
            self.mascotas.append(mascota)
            mascota.propietario = self

    def __str__(self):
        return f'Nombre: {self.nombre} - Contacto: {self.contacto}'

    @classmethod
    def from_dict(cls, datos: Dict, veterinarios: List):
        """Reconstruye un cliente desde diccionario"""
        cliente = cls(
            datos['nombre'],
            datos['contacto'],
            datos['direccion']
        )
        # Reconstruir mascotas
        for mascota_data in datos.get('mascotas', []):
            mascota = Mascota.from_dict(mascota_data, veterinarios)
            mascota.propietario = cliente
            cliente.mascotas.append(mascota)
            
        return cliente

    def to_dict(self):
        """Serializa el cliente incluyendo sus mascotas"""
        datos = {
            'nombre': self.nombre,
            'contacto': self.contacto,
            'direccion': self.direccion,
            'mascotas': [m.to_dict() for m in self.mascotas]
        }
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

# Modificación en la clase Cita
class Cita:
    def __init__(self, mascota, fecha: datetime, veterinario: Veterinario, servicio: Servicio):
        if mascota is None:
            raise ValueError("La mascota no puede ser None")
        if veterinario is None:
            raise ValueError("El veterinario no puede ser None")
        if servicio is None:
            raise ValueError("El servicio no puede ser None")
        if fecha is None:
            raise ValueError("La fecha no puede ser None")
            
        self.mascota = mascota
        self.fecha = fecha
        self.veterinario = veterinario
        self.servicio = servicio

    def to_dict(self):
        """Serializa la cita a diccionario"""
        if self.mascota is None or self.mascota.nombre is None:
            raise ValueError("Datos de mascota inválidos en la cita")
        if self.mascota.propietario is None or self.mascota.propietario.nombre is None:
            raise ValueError("Datos de propietario inválidos en la cita")
        if self.veterinario is None or self.veterinario.nombre is None:
            raise ValueError("Datos de veterinario inválidos en la cita")
            
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
        if not datos:
            raise ValueError("Datos de cita vacíos")
            
        # Buscar mascota
        mascota = None
        for cliente in clientes:
            for m in cliente.mascotas:
                if m.nombre == datos.get('mascota_nombre') and cliente.nombre == datos.get('cliente_nombre'):
                    mascota = m
                    break
            if mascota:
                break
                
        if mascota is None:
            raise ValueError(f"No se encontró la mascota {datos.get('mascota_nombre')} del cliente {datos.get('cliente_nombre')}")
                
        # Buscar veterinario
        veterinario = next((v for v in veterinarios if v.nombre == datos.get('veterinario')), None)
        if veterinario is None:
            raise ValueError(f"No se encontró el veterinario {datos.get('veterinario')}")
            
        try:
            fecha = datetime.strptime(datos.get('fecha'), "%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            raise ValueError("Formato de fecha inválido")
            
        try:
            servicio = Servicio(datos.get('servicio'))
        except (ValueError, TypeError):
            raise ValueError("Servicio inválido")
            
        return cls(mascota, fecha, veterinario, servicio)

# ------- Clase para la mascota --------------------

# Modificar la clase Mascota para manejar mejor las referencias circulares
class Mascota:
    def __init__(self, nombre: str, especie: str, raza: str, edad: int, propietario: Cliente = None):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.propietario = propietario
        self.historial: List[Cita] = []

    def agregar_cita(self, cita: Cita):
        """Agrega una cita al historial de la mascota"""
        if cita not in self.historial:
            self.historial.append(cita)

    def __str__(self):
        return f'Nombre: {self.nombre} - Especie: {self.especie} - Raza: {self.raza}'

    @classmethod
    def from_dict(cls, datos: Dict, veterinarios: List[Veterinario]):
        """Reconstruye mascota desde diccionario"""
        mascota = cls(
            datos['nombre'],
            datos['especie'],
            datos['raza'],
            datos['edad']
        )
        # El historial se cargará después para evitar referencias circulares
        return mascota

    def to_dict(self):
        """Serializa la mascota incluyendo su historial"""
        return {
            'nombre': self.nombre,
            'especie': self.especie,
            'raza': self.raza,
            'edad': self.edad,
            'historial': [c.to_dict() for c in self.historial if c is not None]
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
        
        try:
            cliente = self.seleccionar_cliente()
            if not cliente:
                return
            
            mascota = self.seleccionar_mascota(cliente)
            if not mascota:
                return

            veterinario = self.seleccionar_veterinario()
            if not veterinario:
                return

            fecha_str = input("Fecha y hora (DD/MM/AAAA HH:MM): ").strip()
            try:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            except ValueError:
                print('Formato de fecha inválido, Use DD/MM/AAAA HH:MM')
                return

            print("\nServicios disponibles: ")
            tabla = PrettyTable()
            tabla.field_names = ["ID", "Nombre"]
            for id_, servicio in enumerate(Servicio.listar(), start=1):
                tabla.add_row([f'{id_}', f'{servicio}'])
            print(tabla)

            try:
                seleccion = int(input("Seleccione servicio: ")) - 1
                if seleccion < 0 or seleccion >= len(Servicio.listar()):
                    raise ValueError("Selección fuera de rango")
                servicio = Servicio(Servicio.listar()[seleccion])
            except (ValueError, IndexError):
                print("Selección inválida")
                return

            nueva_cita = Cita(mascota, fecha, veterinario, servicio)
            mascota.agregar_cita(nueva_cita)
            self.veterinaria.citas.append(nueva_cita)
            print(f'Cita programada para {mascota.nombre} el {fecha_str}')
            
        except Exception as e:
            print(f"Error al programar la cita: {e}")
                
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
