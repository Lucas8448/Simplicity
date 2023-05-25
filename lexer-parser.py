import re
import copy
import math

TOKEN_TYPES = [
    ('COMMENT', r'//.*'),
    ('KEYWORD', r'\b(var|func|return|print)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'[=+\-/*<>!&|^]'),
    ('INTEGER', r'\b\d+\b'),
    ('WHITESPACE', r'\s+'),
    ('NEWLINE', r'\n'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LCURLY', r'\{'),
    ('RCURLY', r'\}'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('DOT', r'\.')
]

OPERATORS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    '^': lambda x, y: x ** y,
}

def lexer(input):
    pos = 0
    tokens = []

    while pos < len(input):
        match = None
        for token_type, regex in TOKEN_TYPES:
            pattern = re.compile(regex)
            match = pattern.match(input, pos)
            if match:
                token_value = match.group(0)
                if token_type not in ('WHITESPACE', 'COMMENT'):
                    tokens.append((token_type, token_value))
                pos += len(token_value)
                break
        
        if not match:
            print(f'Invalid character at position {pos}')
            break

    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbols = {}
        self.functions = {
            'sum': lambda x, y: x + y,
            'difference': lambda x, y: x - y,
            'product': lambda x, y: x * y,
            'quotient': lambda x, y: x / y,
            'square': lambda x: x ** 2,
            'sqrt': lambda x: x ** 0.5,
            'sin': lambda x: math.sin(x),
            'cos': lambda x: math.cos(x),
            'tan': lambda x: math.tan(x),
            'log': lambda x: math.log(x),
            'exp': lambda x: math.exp(x),
            'floor': lambda x: math.floor(x),
            'ceil': lambda x: math.ceil(x),
            'round': lambda x: round(x),
            'abs': lambda x: abs(x),
            'max': lambda x, y: max(x, y),
            'min': lambda x, y: min(x, y)
        }
        self.values = {
            'pi': math.pi,
            'e': math.e,
            'g': 9.81,
        }


    def eat(self, token_type):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == token_type:
            self.pos += 1
        else:
            raise Exception(f'Unexpected token type: {token_type}')

    def parse(self):
        while self.pos < len(self.tokens):
            result = self.statement()
            if result is not None:
                return result

    def statement(self):
        if self.tokens[self.pos][0] == 'KEYWORD':
            if self.tokens[self.pos][1] == 'var':
                self.var_declaration()
            elif self.tokens[self.pos][1] == 'func':
                self.func_declaration()
            elif self.tokens[self.pos][1] == 'return':
                return self.return_statement()
            elif self.tokens[self.pos][1] == 'print':
                self.print_statement()
        elif self.tokens[self.pos][0] == 'IDENTIFIER':
            self.assignment()

    def var_declaration(self):
        self.eat('KEYWORD')  # var
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')  # =
        value = self.expression()
        self.symbols[identifier] = value
        self.eat('SEMICOLON')

    def func_declaration(self):
        self.eat('KEYWORD')  # func
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('LPAREN')
        parameters = []
        while self.tokens[self.pos][0] != 'RPAREN':
            if self.tokens[self.pos][0] == 'IDENTIFIER':
                parameters.append(self.tokens[self.pos][1])
                self.eat('IDENTIFIER')
            if self.tokens[self.pos][0] == 'COMMA':
                self.eat('COMMA')
        self.eat('RPAREN')
        self.eat('LCURLY')
        body = []
        while self.tokens[self.pos][0] != 'RCURLY':
            body.append(copy.deepcopy(self.tokens[self.pos]))
            self.eat(self.tokens[self.pos][0])
        self.eat('RCURLY')
        self.functions[identifier] = (parameters, body)

    def expression(self):
        value = self.term()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATOR' and self.tokens[self.pos][1] in '+-':
            op = self.tokens[self.pos][1]
            self.eat('OPERATOR')
            value2 = self.term()
            value = OPERATORS[op](value, value2)
        return value

    def term(self):
        value = self.factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OPERATOR' and self.tokens[self.pos][1] in '*/^':
            op = self.tokens[self.pos][1]
            self.eat('OPERATOR')
            value2 = self.factor()
            value = OPERATORS[op](value, value2)
        return value

    def factor(self):
        if self.tokens[self.pos][0] == 'INTEGER':
            value = int(self.tokens[self.pos][1])
            self.eat('INTEGER')
        elif self.tokens[self.pos][0] == 'OPERATOR':
            op = self.tokens[self.pos][1]
            if op == '!':
                self.eat('OPERATOR')
                value = self.factorial(self.factor())
            else:
                raise Exception(f'Invalid expression: {self.tokens[self.pos]}')
        elif self.tokens[self.pos][0] == 'IDENTIFIER':
            if self.tokens[self.pos+1][0] == 'LPAREN':
                value = self.function_call()
            else:
                identifier = self.tokens[self.pos][1]
                if identifier in self.symbols:
                    value = self.symbols[identifier]
                elif identifier in self.values:  # check if it's a constant value
                    value = self.values[identifier]
                else:
                    raise Exception(f'Undefined identifier: {identifier}')
                self.eat('IDENTIFIER')
        else:
            raise Exception(f'Invalid expression: {self.tokens[self.pos]}')
        return value


    def return_statement(self):
        self.eat('KEYWORD')  # return
        value = self.expression()
        self.eat('SEMICOLON')
        return value

    def print_statement(self):
        self.eat('KEYWORD')  # print
        value = self.expression()
        print(value)
        self.eat('SEMICOLON')

    def function_call(self):
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('LPAREN')
        arguments = []
        while self.tokens[self.pos][0] != 'RPAREN':
            arguments.append(self.expression())
            if self.tokens[self.pos][0] == 'COMMA':
                self.eat('COMMA')
        self.eat('RPAREN')
        if identifier not in self.functions:
            raise Exception(f'Undefined function: {identifier}')
        if isinstance(self.functions[identifier], tuple):  # user-defined functions
            parameters, body = self.functions[identifier]
            if len(arguments) != len(parameters):
                raise Exception(f'Argument mismatch for function: {identifier}')
            old_pos = self.pos
            old_tokens = self.tokens
            old_symbols = copy.deepcopy(self.symbols)
            self.symbols.update(zip(parameters, arguments))
            self.pos = 0
            self.tokens = body
            result = self.parse()
            self.pos = old_pos
            self.tokens = old_tokens
            self.symbols = old_symbols
            return result
        else:  # built-in functions
            func = self.functions[identifier]
            return func(*arguments)


    def assignment(self):
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')  # =
        value = self.expression()
        self.symbols[identifier] = value
        self.eat('SEMICOLON')

    def factorial(self, value):
        return math.factorial(value)


# get content from test.own
tokens = lexer(open('test.txt').read())
parser = Parser(tokens)
parser.parse()