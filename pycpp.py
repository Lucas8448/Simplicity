import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, rules, skip_whitespace=True):
        self.rules = rules
        self.skip_whitespace = skip_whitespace

    def input(self, buf):
        self.buf = buf
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buf):
            return None

        if self.skip_whitespace:
            while self.pos < len(self.buf) and self.buf[self.pos].isspace():
                self.pos += 1

        if self.pos >= len(self.buf):
            return None

        for token_type, pattern in self.rules:
            match = re.match(pattern, self.buf[self.pos:])
            if match:
                value = match.group()
                tok = Token(token_type, value, 1, self.pos + 1)
                self.pos += len(value)
                return tok

        illegal_char = self.buf[self.pos]
        raise LexerError(
            f'Illegal character "{illegal_char}" at index {self.pos}')

    def tokens(self):
        while True:
            tok = self.token()
            if tok is None:
                break
            yield tok


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = next(self.tokens, None)

    def eat(self, token_type):
        if self.current is not None and self.current.type == token_type:
            self.current = next(self.tokens, None)
        else:
            raise ParserError(f'Unexpected token: {self.current}')

    def parse(self):
        if self.current is not None and self.current.type == 'KEYWORD' and self.current.value == 'int':
            self.eat('KEYWORD')
            if self.current is not None and self.current.type == 'IDENTIFIER':
                name = self.current.value
                self.eat('IDENTIFIER')
                if self.current is not None and self.current.type == 'LPAREN':
                    self.eat('LPAREN')
                    parameters = self.parse_parameters()
                    if self.current is not None and self.current.type == 'RPAREN':
                        self.eat('RPAREN')
                        if self.current is not None and self.current.type == 'LBRACE':
                            self.eat('LBRACE')
                            body = self.parse_body()
                            if self.current is not None and self.current.type == 'RBRACE':
                                self.eat('RBRACE')
                                return ('FUNCTION', name, parameters, body)
        raise ParserError(f'Unexpected token: {self.current}')

    def parse_parameters(self):
        parameters = []
        while self.current is not None and self.current.type != 'RPAREN':
            if self.current.type == 'KEYWORD':
                param_type = self.current.value
                self.eat('KEYWORD')
                if self.current.type == 'IDENTIFIER':
                    param_name = self.current.value
                    self.eat('IDENTIFIER')
                    parameters.append((param_type, param_name))
                else:
                    raise ParserError(
                        f'Invalid parameter name: {self.current}')
            if self.current is not None and self.current.type == 'COMMA':
                self.eat('COMMA')
        return parameters

    def parse_body(self):
        body = []
        while self.current and self.current.type != 'RBRACE':
            if self.current.type == 'KEYWORD' and self.current.value == 'return':
                self.eat('KEYWORD')
                expression = self.parse_expression()
                body.append(('RETURN', expression))
                if self.current and self.current.type == 'SEMICOLON':
                    self.eat('SEMICOLON')
            elif self.current.type == 'IDENTIFIER':
                assignment = self.parse_assignment()
                body.append(assignment)
                if self.current and self.current.type == 'SEMICOLON':
                    self.eat('SEMICOLON')
            if self.current and self.current.type != 'RBRACE':
                # Consume the semicolon after an expression statement if present
                self.eat('SEMICOLON')
        return body

    def parse_expression(self):
        if self.current.type == 'NUMBER':
            left = self.current.value
            self.eat('NUMBER')
            if self.current.type in ('PLUS', 'MINUS', 'MULT', 'DIV'):
                operator = self.current.type
                self.eat(operator)
                if self.current.type == 'NUMBER':
                    right = self.current.value
                    self.eat('NUMBER')
                    return ('EXPR', left, operator, right)
        raise ParserError(f'Invalid expression: {self.current}')

    def parse_assignment(self):
        if self.current.type == 'IDENTIFIER':
            identifier = self.current.value
            self.eat('IDENTIFIER')
            if self.current.type == 'EQUALS':
                self.eat('EQUALS')
                expression = self.parse_expression()
                if self.current.type == 'SEMICOLON':
                    self.eat('SEMICOLON')
                    return ('ASSIGNMENT', identifier, expression)
                else:
                    raise ParserError(
                        'Missing semicolon at the end of assignment')
            else:
                # If the assignment operator is missing, treat it as an expression statement
                return ('EXPRESSION', identifier)
        else:
            raise ParserError(f'Invalid assignment: {self.current}')


rules = [
    ('KEYWORD', r'\bint\b'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('EQUALS', r'='),
    ('NUMBER', r'\b\d+\b'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MULT', r'\*'),
    ('DIV', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('REL_OP', r'[><]=?|=='),
]

try:
    lx = Lexer(rules, skip_whitespace=True)
    lx.input("""
        int add(int a, int b) {
            return a + b;
        }

        int subtract(int a, int b) {
            return a - b;
        }

        int main() {
            int x = add(5, 3);
            int y = subtract(x, 2);
            if (y > 5) {
                y = y - 5;
            } else {
                y = y + 5;
            }
            return 0;
        }
    """)

    tokens = list(lx.tokens())

    parser = Parser(iter(tokens))
    print(parser.parse())
except LexerError as e:
    print(f'LexerError at position {e.args}')
except ParserError as e:
    print(f'ParserError: {e.args}')