# Introducción a Docker: Guía de Aprendizaje y Configuración

Este repositorio contiene mis apuntes, prácticas y configuración de Docker realizados durante el tercer semestre de la Tecnicatura en Programación (UTN).

## 📝 Descripción
Docker permite crear, desplegar y ejecutar aplicaciones dentro de contenedores. El objetivo de esta práctica es comprender el ciclo de vida de los contenedores y cómo agilizar el entorno de desarrollo tanto en Linux como en Windows.

## 🛠️ Instalación

### En Linux (Mi entorno: Linux Mint)
Dado que trabajo en un entorno basado en Debian/Ubuntu, los pasos seguidos fueron:

1. **Actualizar el sistema:**
   ```bash
   sudo apt update && sudo apt upgrade
Instalar dependencias:

Bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common
Agregar la llave GPG oficial de Docker:

Bash
curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
Instalar Docker Engine:

Bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
Verificar instalación:

Bash
sudo docker --version
En Windows (Entorno alternativo)
Para quienes utilicen Windows (usando WSL2, que es la práctica recomendada):

Descargar e instalar Docker Desktop desde el sitio oficial.

Asegurarse de tener habilitada la característica de WSL 2 (Windows Subsystem for Linux).

En la configuración de Docker Desktop, activar la integración con la distribución de Linux que utilices (ej. Ubuntu).

🚀 Uso Básico
Comandos esenciales que utilizo para mis prácticas:

Listar imágenes descargadas: docker images

Correr un contenedor nuevo: docker run nombre_imagen

Ver contenedores activos: docker ps

Detener un contenedor: docker stop id_contenedor

Eliminar un contenedor: docker rm id_contenedor

💡 Notas de Aprendizaje
Contenedores vs Máquinas Virtuales: Aprendí que los contenedores comparten el kernel del sistema operativo, lo que los hace mucho más ligeros y rápidos.

Dockerfile: Es el archivo receta que define qué va dentro de mi contenedor.

Persistencia: Es vital usar "Volumes" para que los datos no se borren al destruir el contenedor.

📚 Recursos consultados
Pelado Nerd - Docker desde cero

HolaMundo - Tutoriales de Docker

Documentación oficial de Docker (docs.docker.com)

Documentado por: Ariel Mazara | Equipo Código Crítico

