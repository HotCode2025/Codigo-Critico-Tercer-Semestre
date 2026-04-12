resultado = None

try:
    a = int(input('Digite el primer numero: '))
    b = int(input('Digite el segundo numero: '))
    resultado = a / b # modificamos
except TypeError as e:
    print(f'TypeError - Ocurrio un error: {type(e)}')
except ZeroDivisionError as e:
    print(f'ZeroDivisionError - Ocurrio un error: {type(e)}') ##variable e se puede cambiar
except Exception as e:  ##Debe ir al final siempre esta clase ##utilizar la clase padre siempre porque con Zerodivisionerror da error lo mas generico.
    print(f' Exception - Ocurrio un error: {type(e)}') ## La nombramos con la variale e

print(f'Resultado: {resultado}')
print('seguimos...')