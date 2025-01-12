import re
import copy
import math

TOKEN_TYPES = [
    ('COMMENT', r'//.*'),
    ('KEYWORD', r'\b(var|func|return|print|for|to)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'[=+\-/*<>!&|^]+'),
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
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x >= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y,
    '&': lambda x, y: x and y,
    '|': lambda x, y: x or y,
    '!': lambda x: not x,
    '^': lambda x, y: x ** y
}

KNOWN_KEYWORDS_FUNCTIONS = [
    'var', 'func', 'return', 'print', 
    'sum', 'difference', 'product', 'quotient', 
    'square', 'sqrt', 'sin', 'cos', 'tan', 'log', 
    'exp', 'floor', 'ceil', 'round', 'abs', 'max', 
    'min', 'and', 'or', 'not'
]

def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def closest_match(token, known_keywords_functions):
    closest_token = min(known_keywords_functions, key=lambda t: levenshtein_distance(token, t))
    return closest_token

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
            start = pos
            while pos < len(input) and not input[pos].isspace():
                pos += 1
            unrecognized_token = input[start:pos]
            suggestion = closest_match(unrecognized_token, KNOWN_KEYWORDS_FUNCTIONS)
            print(f'Unrecognized token "{unrecognized_token}" at position {start}. Did you mean "{suggestion}"?')
            return tokens  # Return the tokens we have so far

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
            'ln': lambda x: math.log(x),
            'lg': lambda x: math.log10(x),
            'log': lambda x, y: math.log(x, y),
            'exp': lambda x: math.exp(x),
            'floor': lambda x: math.floor(x),
            'ceil': lambda x: math.ceil(x),
            'round': lambda x: round(x),
            'abs': lambda x: abs(x),
            'max': lambda x, y: max(x, y),
            'min': lambda x, y: min(x, y),
            'and': lambda x, y: x and y,
            'or': lambda x, y: x or y,
            'not': lambda x: not x,
            'pythagoras': lambda x, y: (x ** 2 + y ** 2) ** 0.5,
        }
        self.values = {
            'pi': math.pi,
            'e': math.e,
            'g': 9.80665, # at ground level
            'u': 1.66*10^(-27), #kilograms
            'bsk': 2*10^(-7), # biot-savart const
            'ke': 8.99*10^9, # columb const
            'ec': 1.602*10^(-19),
            'gamma': 6.67*10^(-11),
            'c': 299792458, # speed of light
            'h': 6.63*10^(-34), # planck const
            'B': 2.18*10^(-18)
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
            elif self.tokens[self.pos][1] == 'for':
                self.for_loop()
        elif self.tokens[self.pos][0] == 'IDENTIFIER':
            self.assignment()

    def var_declaration(self):
        self.eat('KEYWORD')
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')
        value = self.expression()
        self.symbols[identifier] = value
        self.eat('SEMICOLON')

    def func_declaration(self):
        self.eat('KEYWORD')
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

    def for_loop(self):
        self.eat('KEYWORD')
        loop_var = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')
        start_val = self.expression()
        self.eat('KEYWORD')
        end_val = self.expression()
        self.eat('LCURLY')
        loop_body = []
        while self.tokens[self.pos][0] != 'RCURLY':
            loop_body.append(copy.deepcopy(self.tokens[self.pos]))
            self.eat(self.tokens[self.pos][0])
        self.eat('RCURLY')

        for i in range(start_val, end_val + 1):
            self.symbols[loop_var] = i
            old_pos = self.pos
            old_tokens = self.tokens
            self.pos = 0
            self.tokens = loop_body
            self.parse()
            self.pos = old_pos
            self.tokens = old_tokens

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
                elif identifier in self.values:
                    value = self.values[identifier]
                else:
                    raise Exception(f'Undefined identifier: {identifier}')
                self.eat('IDENTIFIER')
        else:
            raise Exception(f'Invalid expression: {self.tokens[self.pos]}')
        return value


    def return_statement(self):
        self.eat('KEYWORD')
        value = self.expression()
        self.eat('SEMICOLON')
        return value

    def print_statement(self):
        self.eat('KEYWORD')
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
        if isinstance(self.functions[identifier], tuple):
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
        else:
            func = self.functions[identifier]
            return func(*arguments)


    def assignment(self):
        identifier = self.tokens[self.pos][1]
        self.eat('IDENTIFIER')
        self.eat('OPERATOR')
        value = self.expression()
        self.symbols[identifier] = value
        self.eat('SEMICOLON')

    def factorial(self, value):
        return math.factorial(value)


tokens = lexer(open('test.sply').read())
parser = Parser(tokens)
parser.parse()
