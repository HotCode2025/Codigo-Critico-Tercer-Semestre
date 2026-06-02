#!/bin/bash

# Archivo que actuará como base de datos
ARCHIVO="usuarios.txt"

# Crear el archivo si no existe
if [ ! -f "$ARCHIVO" ]; then
    touch "$ARCHIVO"
fi

# Bucle principal para el menú
while true; do
    echo "---------------------------------------------------"
    echo "              ADMINISTRACIÓN DE USUARIOS           "
    echo "---------------------------------------------------"
    echo "1. Agregar un usuario"
    echo "2. Listar usuarios"
    echo "3. Buscar un usuario"
    echo "4. Eliminar un usuario"
    echo "5. Salir"
    echo "---------------------------------------------------"
    read -p "Elige una opción (1-5): " opcion
    echo ""

    case $opcion in
        1)
            # Agregar un usuario
            read -p "Introduce el nombre del nuevo usuario: " nuevo_usuario
            
            # Validar que no esté vacío
            if [ -z "$nuevo_usuario" ]; then
                echo "Error: El nombre de usuario no puede estar vacío."
            else
                # Comprobar si el usuario ya existe (coincidencia exacta de línea)
                if grep -q -x "$nuevo_usuario" "$ARCHIVO"; then
                    echo "Error: El usuario '$nuevo_usuario' ya existe."
                else
                    echo "$nuevo_usuario" >> "$ARCHIVO"
                    echo "Éxito: Usuario '$nuevo_usuario' agregado correctamente."
                fi
            fi
            echo ""
            ;;
            
        2)
            # Listar usuarios
            echo "--- Lista de Usuarios ---"
            # Verificar si el archivo tiene tamaño mayor a 0
            if [ -s "$ARCHIVO" ]; then
                cat "$ARCHIVO"
            else
                echo "No hay usuarios registrados en el sistema."
            fi
            echo "-------------------------"
            echo ""
            ;;
            
        3)
            # Buscar un usuario
            read -p "Introduce el nombre del usuario a buscar: " buscar_usuario
            
            if [ -z "$buscar_usuario" ]; then
                echo "Error: El nombre de usuario no puede estar vacío."
            else
                if grep -q -x "$buscar_usuario" "$ARCHIVO"; then
                    echo "Resultado: El usuario '$buscar_usuario' se encuentra en la base de datos."
                else
                    echo "Resultado: El usuario '$buscar_usuario' NO existe."
                fi
            fi
            echo ""
            ;;
            
        4)
            # Eliminar un usuario
            read -p "Introduce el nombre del usuario a eliminar: " eliminar_usuario
            
            if [ -z "$eliminar_usuario" ]; then
                echo "Error: El nombre de usuario no puede estar vacío."
            else
                # Comprobar primero si existe
                if grep -q -x "$eliminar_usuario" "$ARCHIVO"; then
                    # Pedir confirmación
                    read -p "¿Estás seguro de que deseas eliminar a '$eliminar_usuario'? (s/n): " confirmacion
                    if [[ "$confirmacion" == "s" || "$confirmacion" == "S" ]]; then
                        # Eliminar la línea exacta que contiene el usuario y guardar en un archivo temporal
                        grep -v -x "$eliminar_usuario" "$ARCHIVO" > temp.txt
                        mv temp.txt "$ARCHIVO"
                        echo "Éxito: Usuario '$eliminar_usuario' eliminado."
                    else
                        echo "Operación cancelada."
                    fi
                else
                    echo "Error: El usuario '$eliminar_usuario' no existe."
                fi
            fi
            echo ""
            ;;
            
        5)
            # Salir
            echo "Saliendo del administrador de usuarios..."
            exit 0
            ;;
            
        *)
            # Opción inválida
            echo "Opción no válida. Por favor, elige un número del 1 al 5."
            echo ""
            ;;
    esac
done
