#!/bin/bash

# Bucle infinito para mostrar el menú repetitivamente
while true; do
    echo ""
    echo "======================================"
    echo "          GESTOR DE ARCHIVOS"
    echo "======================================"
    echo "1. Crear un archivo"
    echo "2. Eliminar un archivo"
    echo "3. Listar archivos del directorio actual"
    echo "4. Mostrar el tamaño de un archivo"
    echo "5. Salir"
    echo "======================================"
    read -p "Seleccione una opción: " opcion
    echo ""

    # Estructura case para manejar las opciones
    case $opcion in
        1)
            read -p "Ingrese el nombre del archivo a crear: " nombre_archivo
            touch "$nombre_archivo"
            echo "-> Archivo '$nombre_archivo' creado con éxito."
            ;;
        2)
            read -p "Ingrese el nombre del archivo a eliminar: " nombre_archivo
            # Verificamos si el archivo realmente existe antes de preguntar
            if [ -f "$nombre_archivo" ]; then
                read -p "¿Está seguro de que desea eliminar '$nombre_archivo'? (s/n): " confirmacion
                if [[ "$confirmacion" == "s" || "$confirmacion" == "S" ]]; then
                    rm "$nombre_archivo"
                    echo "-> Archivo eliminado."
                else
                    echo "-> Operación cancelada."
                fi
            else
                echo "-> Error: El archivo '$nombre_archivo' no existe."
            fi
            ;;
        3)
            echo "-> Listando archivos del directorio actual:"
            ls -lh
            ;;
        4)
            read -p "Ingrese el nombre del archivo para ver su tamaño: " nombre_archivo
            if [ -f "$nombre_archivo" ]; then
                # du -sh muestra el tamaño en formato legible (KB, MB, etc.)
                tamano=$(du -sh "$nombre_archivo" | cut -f1)
                echo "-> El tamaño de '$nombre_archivo' es: $tamano"
            else
                echo "-> Error: El archivo no existe o es un directorio."
            fi
            ;;
        5)
            echo "Saliendo del programa... ¡Hasta luego!"
            break # Rompe el bucle para terminar el script
            ;;
        *)
            # Si ingresa cualquier otra cosa, muestra el error
            echo "-> ERROR: Opción inválida. Por favor, seleccione un número del 1 al 5."
            ;;
    esac
done
