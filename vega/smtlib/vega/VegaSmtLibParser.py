from ...Exceptions import ExecutionError
from .helper import split_script_to_lines

from .Fnode import *
from .Command import *
from .SymbolType import SymbolType

class VegaSmtLibParser:
    def __init__(self):
        self.symbols = {}

    def parse_fnode_arg(self, last):
        last = last.strip(' ')
        # print("parse_fnode_arg({})".format(last)) # DEBUG
        if last[0] != '(':
            if ' ' in last:
                arg, last = last.split(' ', 1)
                return arg, last.strip(' ')
            else:
                return last, ""
        else:
            bracket_depth = 0
            arg = ""
            for i, c in enumerate(last):
                if c == '\r' or c == '\n':
                    continue
                arg += c
                if c == '(':
                    bracket_depth += 1
                elif c == ')':
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        # print("arg='{}', last='{}'".format(arg, last[i+1:]))
                        return arg, last[i+1:].strip(' ')
        raise ExecutionError('Reached fail through')

    def parse_fnode(self, line):
        line = line.strip(' ')
        if line == "()":
            return Blank()
        if line[0] == '(' and line[-1] == ')':
            line = line[1:-1]
        # print("parse_fnode({})".format(line)) # DEBUG

        raw_command = line.split(' ', 1)
        
        if len(raw_command) == 1:
            if raw_command[0] in ['true', 'false']:
                return BoolConstant(raw_command[0])
            else:
                symbol_name = raw_command[0]
                symbol_type = self.symbols[symbol_name]
                return Symbol(symbol_name, symbol_type)
        else:
            name, last = raw_command

            args = []
            while last:
                arg, last = self.parse_fnode_arg(last)
                args.append(self.parse_fnode(arg))
            
            map_name_fnode = {
                'and': And,
                'or': Or,
                'not': Not,
                '=>': Implies,
                '=': Equals,
                'ite': Ite,
            }

            if name in map_name_fnode:
                return map_name_fnode[name](name, args)
            elif name == 'distinct':
                return Not(name, [Equals(name, args)])
            else:
                return Fnode(name, args)

    def parse_command(self, line):
        line = line.strip(' ')
        if line[0] == '(' and line[-1] == ')':
            line = line[1:-1]
        
        if ' ' in line:
            name, last = line.split(' ', 1)
            
            if name in ['set-info']:
                return Command(name, last.split(' '))
            
            elif name == 'declare-datatypes':
                last_replace_split = last.strip(' ').replace('(', '').replace(')', '').split(' ')
                datatype_name = last_replace_split[1]
                datatype_values = last_replace_split[2:]
                for value in datatype_values:
                    self.symbols[value] = SymbolType(datatype_name)
                return Command(name, [DataType(datatype_name, datatype_values)])
            
            elif name == 'declare-fun':
                last_replace_split = last.strip(' ').replace('(', '').replace(')', '').split(' ')
                symbol_name = last_replace_split[0]
                symbol_type = last_replace_split[2]
                self.symbols[symbol_name] = SymbolType(symbol_type)
                return Command(name, [])
            else:
                return Command(name, self.parse_fnode(line).args())
        
        else:
            name = line
            return Command(name, [])

    def get_script(self, raw_script):
        script = []
        for line in split_script_to_lines(raw_script):
            script.append(self.parse_command(line))
        return script