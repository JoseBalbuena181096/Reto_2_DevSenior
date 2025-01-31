# Sistema de Gestión de Veterinaria 🐾

Un sistema completo de gestión para clínicas veterinarias desarrollado en Python, con persistencia de datos en JSON. Este proyecto permite administrar clientes, mascotas, citas y personal veterinario de manera eficiente.

## Características 🌟

- Gestión de clientes y sus mascotas
- Registro y seguimiento de citas médicas
- Administración de personal veterinario
- Historial médico por mascota
- Persistencia de datos en formato JSON
- Interfaz de línea de comandos intuitiva
- Validación robusta de datos de entrada

## Requisitos 📋

- Python 3.6 o superior
- Biblioteca `prettytable` para la visualización de datos

Para instalar las dependencias:
```bash
pip install prettytable
```

## Instalación 🔧

1. Clona el repositorio:
```bash
git clone https://github.com/JoseBalbuena181096/Reto_2_DevSenior
```

2. Navega al directorio del proyecto:
```bash
cd reto_2_devsenior
```

3. Ejecuta el programa:
```bash
python main.py
```

## Uso 💻

El sistema ofrece las siguientes opciones principales:

1. **Registrar Cliente**: Añade nuevos clientes al sistema
2. **Registrar Mascota**: Asocia mascotas a clientes existentes
3. **Programar Cita**: Agenda nuevas citas médicas
4. **Consultar Historial**: Revisa el historial médico de las mascotas
5. **Listar Clientes**: Muestra todos los clientes registrados
6. **Registrar Veterinario**: Añade nuevos veterinarios al sistema
7. **Salir**: Guarda los cambios y cierra el programa

## Estructura del Proyecto 📁

- `main.py`: Archivo principal del programa
- `datos_veterinaria.json`: Almacenamiento persistente de datos
- `README.md`: Documentación del proyecto

### Clases Principales

- `Veterinaria`: Singleton para gestionar toda la aplicación
- `Persona`: Clase base para clientes y veterinarios
- `Cliente`: Gestión de información de clientes
- `Veterinario`: Manejo de personal veterinario
- `Mascota`: Administración de mascotas y su historial
- `Cita`: Control de citas médicas
- `Menu`: Interfaz de usuario y validaciones

## Características de Seguridad 🔒

- Validación exhaustiva de datos de entrada
- Respaldo automático de datos antes de guardar
- Manejo de errores robusto
- Límites de intentos en entradas de usuario

## Contribución 🤝

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un Fork del proyecto
2. Crea una nueva rama (`git checkout -b feature/AmazingFeature`)
3. Realiza tus cambios y haz commit (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Autor ✒️

- **José Ángel Balbuena Palma** - *Desarrollo Inicial*
-  Ver video de funcionamiento  [AQUÍ](https://www.youtube.com/watch?v=711KrOxIIcA) 

## Licencia 📄

Este proyecto está bajo la Licencia [MIT](https://opensource.org/licenses/MIT) - mira el archivo LICENSE.md para detalles

## Agradecimientos 💎

- A todos los que usen y mejoren este código
- A la comunidad de desarrolladores Python

---
⌨️ con ❤️ por [José Ángel Balbuena Palma](https://github.com/JoseBalbuena181096) 😊