import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

class TokenType(Enum):
    # Palabras clave
    IF, ELIF, ELSE, WHILE, FOR, IN, DEF, RETURN = "IF", "ELIF", "ELSE", "WHILE", "FOR", "IN", "DEF", "RETURN"
    PASS, BREAK, CONTINUE, TRUE, FALSE, NONE = "PASS", "BREAK", "CONTINUE", "TRUE", "FALSE", "NONE"
    AND, OR, NOT, NOT_IN, IS, IS_NOT = "AND", "OR", "NOT", "NOT_IN", "IS", "IS_NOT"
    # Identificadores y literales
    IDENT, NUMBER, STRING = "IDENT", "NUMBER", "STRING"
    # Operadores aritméticos
    PLUS, MINUS, MULTIPLY, DIVIDE = "PLUS", "MINUS", "MULTIPLY", "DIVIDE"
    FLOOR_DIVIDE, MODULO, POWER = "FLOOR_DIVIDE", "MODULO", "POWER"
    # Operadores relacionales
    EQUAL, NOT_EQUAL, LESS_THAN, LESS_EQUAL = "EQUAL", "NOT_EQUAL", "LESS_THAN", "LESS_EQUAL"
    GREATER_THAN, GREATER_EQUAL = "GREATER_THAN", "GREATER_EQUAL"
    # Operadores de asignación
    ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN = "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN"
    MULT_ASSIGN, DIV_ASSIGN = "MULT_ASSIGN", "DIV_ASSIGN"
    # Signos de puntuación
    LPAREN, RPAREN, LBRACKET, RBRACKET = "LPAREN", "RPAREN", "LBRACKET", "RBRACKET"
    LBRACE, RBRACE, COMMA, COLON, DOT, SEMICOLON = "LBRACE", "RBRACE", "COMMA", "COLON", "DOT", "SEMICOLON"
    # Tokens especiales
    NEWLINE, INDENT, DEDENT, COMMENT, EOF, ERROR = "NEWLINE", "INDENT", "DEDENT", "COMMENT", "EOF", "ERROR"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int    
    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

class MiniPyLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]        
        # Palabras clave del lenguaje
        self.keywords = {
            'if': TokenType.IF, 'elif': TokenType.ELIF, 'else': TokenType.ELSE,
            'while': TokenType.WHILE, 'for': TokenType.FOR, 'in': TokenType.IN,
            'def': TokenType.DEF, 'return': TokenType.RETURN, 'pass': TokenType.PASS,
            'break': TokenType.BREAK, 'continue': TokenType.CONTINUE,
            'and': TokenType.AND, 'or': TokenType.OR, 'not': TokenType.NOT,
            'True': TokenType.TRUE, 'False': TokenType.FALSE, 'None': TokenType.NONE,
            'is': TokenType.IS,
        }        
        # Operadores de múltiples caracteres
        self.multi_char_operators = {
            '//': TokenType.FLOOR_DIVIDE, '**': TokenType.POWER,
            '==': TokenType.EQUAL, '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL, '>=': TokenType.GREATER_EQUAL,
            '+=': TokenType.PLUS_ASSIGN, '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.MULT_ASSIGN, '/=': TokenType.DIV_ASSIGN,
            'not in': TokenType.NOT_IN, 'is not': TokenType.IS_NOT,
        }
        # Operadores de un carácter
        self.single_char_operators = {
            '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE, '%': TokenType.MODULO, '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN, '>': TokenType.GREATER_THAN,
        }
        # Signos de puntuación
        self.punctuation = {
            '(': TokenType.LPAREN, ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE,
            ',': TokenType.COMMA, ':': TokenType.COLON,
            '.': TokenType.DOT, ';': TokenType.SEMICOLON,
        }
    
    def current_char(self) -> Optional[str]:
        return self.text[self.pos] if self.pos < len(self.text) else None
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None
    
    def advance(self):
        if self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def read_number(self) -> Token:
        start_col, num_str = self.column, ""
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()   
        # Chequea por punto decimal
        if (self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit()):
            num_str += self.current_char()
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()        
        return Token(TokenType.NUMBER, num_str, self.line, start_col)
    
    def read_string(self, quote_char: str) -> Token:
        start_col, string_val = self.column, ""
        self.advance()  # Salta la comilla inicial        
        while self.current_char():
            char = self.current_char()
            if char == quote_char:
                self.advance()
                return Token(TokenType.STRING, string_val, self.line, start_col)
            elif char == '\\':
                self.advance()
                if self.current_char():
                    escape_char = self.current_char()
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', quote_char: quote_char}
                    string_val += escape_map.get(escape_char, escape_char)
                    self.advance()
            else:
                string_val += char
                self.advance()
        
        return Token(TokenType.ERROR, "Unterminated string", self.line, start_col)
    
    def read_identifier(self) -> Token:
        start_col, ident_str = self.column, ""
        while (self.current_char() and 
               (self.current_char().isalpha() or self.current_char() == '_' or 
                (len(ident_str) > 0 and self.current_char().isdigit()))):
            ident_str += self.current_char()
            self.advance()
        return Token(self.keywords.get(ident_str, TokenType.IDENT), ident_str, self.line, start_col)
    
    def read_comment(self) -> Token:
        start_col, comment_str = self.column, ""
        while self.current_char() and self.current_char() != '\n':
            comment_str += self.current_char()
            self.advance()
        return Token(TokenType.COMMENT, comment_str, self.line, start_col)
    
    def check_indentation(self, line_text: str) -> List[Token]:
        tokens = []
        indent_level = sum(4 if char == '\t' else 1 for char in line_text if char in ' \t')
        current_level = self.indent_stack[-1]
        
        if indent_level > current_level:
            self.indent_stack.append(indent_level)
            tokens.append(Token(TokenType.INDENT, "", self.line, 1))
        elif indent_level < current_level:
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, "", self.line, 1))
        
        return tokens
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.pos < len(self.text):
            # Manejo de indentación al inicio de línea
            if self.column == 1 and self.current_char() not in ['\n', None]:
                temp_pos = self.pos
                while temp_pos < len(self.text) and self.text[temp_pos] in ' \t':
                    temp_pos += 1
                
                if temp_pos < len(self.text) and self.text[temp_pos] != '\n':
                    line_text = self.text[self.pos:temp_pos]
                    tokens.extend(self.check_indentation(line_text))
            
            self.skip_whitespace()
            if not self.current_char():
                break
                
            char = self.current_char()
            start_col = self.column
            
            # Procesamiento de caracteres específicos
            if char == '\n':
                tokens.append(Token(TokenType.NEWLINE, char, self.line, start_col))
                self.advance()
            elif char == '#':
                tokens.append(self.read_comment())
            elif char.isdigit():
                tokens.append(self.read_number())
            elif char in ['"', "'"]:
                tokens.append(self.read_string(char))
            elif char.isalpha() or char == '_':
                tokens.append(self.read_identifier())
            else:
                # Operadores de múltiples caracteres
                found_multi_op = False
                for op_str, token_type in self.multi_char_operators.items():
                    if self.text[self.pos:].startswith(op_str):
                        tokens.append(Token(token_type, op_str, self.line, start_col))
                        for _ in range(len(op_str)):
                            self.advance()
                        found_multi_op = True
                        break
                
                if not found_multi_op:
                    # Operadores de un carácter y puntuación
                    if char in self.single_char_operators:
                        tokens.append(Token(self.single_char_operators[char], char, self.line, start_col))
                        self.advance()
                    elif char in self.punctuation:
                        tokens.append(Token(self.punctuation[char], char, self.line, start_col))
                        self.advance()
                    else:
                        # Carácter no reconocido
                        tokens.append(Token(TokenType.ERROR, char, self.line, start_col))
                        self.advance()
        
        # Generar DEDENT para niveles restantes
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

def main():
    """Función principal - solo para pruebas directas del módulo"""
    print("Analizador Léxico para Mini-Python")
    print("Ejecute 'python analizador_gui.py' para usar la interfaz gráfica")

if __name__ == "__main__":
    main()
