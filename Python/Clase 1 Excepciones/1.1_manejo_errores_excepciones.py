resultado = None
a = '10'
b = 0
try:
    resultado = a / b # modificamos
except Exception as e:  ##utilizar la clase padre siempre porque con Zerodivisionerror da error lo mas generico.
    print(f'Ocurrio un error: {e}') ## La nombramos con la variale e

print(f'Resultado: {resultado}')
print('seguimos...')