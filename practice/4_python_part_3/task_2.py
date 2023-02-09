"""
Write function which executes custom operation from math module
for given arguments.
Restrition: math function could take 1 or 2 arguments
If given operation does not exists, raise OperationNotFoundException
Examples:
     >>> math_calculate('log', 1024, 2)
     10.0
     >>> math_calculate('ceil', 10.7)
     11
"""
import math

from inspect import getmembers, isbuiltin

math_functions = {f[0]: f[1] for f in getmembers(math, isbuiltin)}

class OperationNotFoundException(Exception):
    pass

class IncorrectAmountOfArgumentsException(Exception):
    pass
def math_calculate(function_name: str, *args):
    if function_name not in math_functions:
        raise OperationNotFoundException
    if 0 > len(args) > 2:
        raise IncorrectAmountOfArgumentsException

    return math_functions[function_name](*args)

"""
Write tests for math_calculate function
"""
