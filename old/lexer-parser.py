import re

TOKEN_TYPES = [
    ('COMMENT', r'//.*'),
    ('KEYWORD', r'\b(var|func|return|if|else)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'[=+\-/*<>!&|]'),
    ('INTEGER', r'\b\d+\b'),
    ('WHITESPACE', r'\s+'),
    ('NEWLINE', r'\n'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LCURLY', r'\{'),
    ('RCURLY', r'\}'),
    ('SEMICOLON', r';'),
]


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

    def eat(self, token_type):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == token_type:
            self.pos += 1
        else:
            raise Exception(f'Unexpected token type: {token_type}')

    def parse(self):
        while self.pos < len(self.tokens):
            self.statement()

    def statement(self):
        if self.tokens[self.pos][0] == 'KEYWORD':
            if self.tokens[self.pos][1] == 'var':
                self.var_declaration()
            elif self.tokens[self.pos][1] == 'func':
                self.func_declaration()
            elif self.tokens[self.pos][1] == 'return':
                return self.return_statement()
        elif self.tokens[self.pos][0] == 'RCURLY':
            return True
        return False

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
        self.eat('RPAREN')
        self.eat('LCURLY')
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] != 'RCURLY':
            self.statement()
        self.eat('RCURLY')

    def expression(self):
        if self.tokens[self.pos][0] == 'INTEGER':
            value = int(self.tokens[self.pos][1])
            self.eat('INTEGER')
        elif self.tokens[self.pos][0] == 'IDENTIFIER':
            identifier = self.tokens[self.pos][1]
            if identifier in self.symbols:
                value = self.symbols[identifier]
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

# get content from test.own
tokens = lexer(open('old/test.txt').read())
parser = Parser(tokens)
parser.parse()
print(parser.symbols)
