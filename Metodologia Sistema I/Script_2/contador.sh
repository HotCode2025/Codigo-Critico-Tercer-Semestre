#!/bin/bash

# 1. Verificar que se hayan pasado exactamente dos parámetros
if [ "$#" -ne 2 ]; then
    echo "Error: Se requieren exactamente dos parámetros."
    echo "Uso: $0 <numero_inicial> <numero_final>"
    exit 1
fi

# 2. Verificar que ambos parámetros sean números (incluyendo negativos)
if ! [[ "$1" =~ ^-?[0-9]+$ ]] || ! [[ "$2" =~ ^-?[0-9]+$ ]]; then
    echo "Error: Ambos parámetros deben ser números enteros válidos."
    exit 1
fi

num1=$1
num2=$2

# Bucle principal para el menú
while true; do
    echo "---------------------------------------------------"
    echo "                    MENÚ"
    echo "---------------------------------------------------"
    echo "1. Contar desde el primer número hasta el segundo"
    echo "2. Mostrar solo los números pares en ese rango"
    echo "3. Mostrar cuántos números hay en el rango"
    echo "4. Salir"
    echo "---------------------------------------------------"
    read -p "Elige una opción (1-4): " opcion
    echo ""

    case $opcion in
        1)
            echo "Contando desde $num1 hasta $num2:"
            if [ "$num1" -le "$num2" ]; then
                for (( i=num1; i<=num2; i++ )); do
                    echo -n "$i "
                done
            else
                # Maneja el caso si el primer número es mayor que el segundo (cuenta regresiva)
                for (( i=num1; i>=num2; i-- )); do
                    echo -n "$i "
                done
            fi
            echo ""
            ;;
            
        2)
            echo "Números pares en el rango de $num1 a $num2:"
            if [ "$num1" -le "$num2" ]; then
                for (( i=num1; i<=num2; i++ )); do
                    if (( i % 2 == 0 )); then
                        echo -n "$i "
                    fi
                done
            else
                for (( i=num1; i>=num2; i-- )); do
                    if (( i % 2 == 0 )); then
                        echo -n "$i "
                    fi
                done
            fi
            echo ""
            ;;
            
        3)
            # El cálculo se hace con un bucle como se solicitó en los requisitos
            contador=0
            if [ "$num1" -le "$num2" ]; then
                for (( i=num1; i<=num2; i++ )); do
                    ((contador++))
                done
            else
                for (( i=num1; i>=num2; i-- )); do
                    ((contador++))
                done
            fi
            echo "Hay un total de $contador números en el rango."
            ;;
            
        4)
            echo "Saliendo del script. ¡Hasta luego!"
            exit 0
            ;;
            
        *)
            echo "Opción no válida. Por favor, elige un número del 1 al 4."
            ;;
    esac
done


