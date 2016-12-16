# -----------------------------------------------------------------
# pycparser: func_defs.py
#
# A transformer for C99 function declarations
#
# Copyright (C) 2016, Rainer Poisel
# License: MIT
# -----------------------------------------------------------------
import sys

from pycparser import c_parser, c_ast, parse_file


class FuncParam(object):
    def __init__(self, dataType, declName):
        self.dataType = dataType
        self.declName = declName


class Function(object):
    def __init__(self, returnType, declName, parameters):
        self.returnType = returnType
        self.declName = declName
        self.parameters = parameters

    def print(self):
        print(self.returnType + ' ' + self.declName, end='')
        print('(', end='')
        for idx in range(len(self.parameters)):
            parameter = self.parameters[idx]
            if parameter.declName is not None:
                print(parameter.dataType + ' ' + parameter.declName, end='')
            else:
                print(parameter.dataType, end='')
            if idx < len(self.parameters) - 1:
                print(", ", end='')
        print(');')


class FuncDeclVisitor(c_ast.NodeVisitor):
    def __init__(self, callback):
        self.callback = callback

    def visit_FuncDecl(self, node):
        self.callback(Function(
            getDataType(node),
            getDeclName(node),
            getParameters(node)
        ))


def getDeclName(node):
    if hasattr(node, 'declname'):
        return node.declname
    if hasattr(node, 'type'):
        return getDeclName(node.type)
    return None  # error


def getDataType(node, typeStr=''):
    if hasattr(node, 'quals') and len(node.quals) > 0:
        typeStr += node.quals[0] + ' '
    if hasattr(node, 'type'):
        curType = getDataType(node.type, typeStr)
        if type(node.type) == c_ast.PtrDecl:
            curType += "*"
        return curType
    return typeStr + node.names[0]


def getParameters(node):
    parameters = []
    for parameter in node.args.params:
        funcParam = FuncParam(getDataType(parameter), getDeclName(parameter))
        parameters.append(funcParam)
    return parameters


def print_func(function):
    function.print()


def iterate_func_decls(filename, includeDirs, callback):
    cppArgs = [u'-I' + includeDir for includeDir in includeDirs]
    ast = parse_file(
        filename,
        use_cpp=True,
        cpp_args=cppArgs
    )

    v = FuncDeclVisitor(callback)
    v.visit(ast)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        print("Usage: " + sys.argv[0] + " <header-file>")
        sys.exit(1)

    includeDirs = [
    ]

    iterate_func_decls(filename, includeDirs, print_func)
