from enum import Enum


class TokenType(Enum):
    OPERATOR = 1
    LEXEME = 2
    OP = 3
    CP = 4
    UNARY_OPERATOR = 5


class Token:
    type: TokenType
    value: str

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"type: {self.type}; value: {self.value}"
