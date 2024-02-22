import exceptions
from tokens import TokenType, Token
from exceptions import WrongSyntaxException
from tree_nodes import TreeNode, NotNode, AndNode, OrNode, LexemeNode


def is_EOF(idx, parsed):
    return idx >= len(parsed)


class TreeBuilder:
    parsed: list[Token]

    def __init__(self, parsed: list[Token]):
        self.parsed = parsed

    def build(self):
        parsed = self.parsed
        idx = 0
        stack = list()
        while not is_EOF(idx, parsed):
            elem = parsed[idx]
            idx = self.__parse_elem(elem, idx, stack)
        return stack.pop()

    def __parse_elem(self, elem, idx, stack):
        """
        :param elem: элемент
        :param idx: индекс элемента
        :param stack: стек для того чтобы положить туда результат
        :return: индекс следующий за обработанным элементом
        """
        if elem.type == TokenType.OP:
            node, idx = self.__parse_parenthesis(idx + 1)
            if node is None:
                raise WrongSyntaxException("Нода отсутствует")
            stack.append(node)
            return idx
        elif elem.type == TokenType.UNARY_OPERATOR:
            if ((not is_EOF(idx + 1, self.parsed) and self.parsed[idx + 1].type == TokenType.OPERATOR)
                    or idx == len(self.parsed) - 1):
                raise WrongSyntaxException("Неверное использование унарного опрератора")
            unary_op_stack = list()
            idx = self.__parse_elem(self.parsed[idx + 1], idx + 1, unary_op_stack)
            stack.append(NotNode(unary_op_stack.pop()))
            return idx
        elif elem.type == TokenType.LEXEME:
            if len(stack) != 0:
                raise WrongSyntaxException("Неверное положение лексемы")
            stack.append(LexemeNode(elem.value))
            return idx + 1
        elif elem.type == TokenType.OPERATOR:
            return self.__parse_operator(elem, idx + 1, stack)
        else:
            raise WrongSyntaxException("Токен имеет неизвестный тип")

    def __parse_parenthesis(self, idx):
        """
        Парсит содержимое скобок.

        :param idx: индекс элемента
        :return: узел, хранящий в себе все операции внутри скобок и индекс следующего элемента
        """
        parsed = self.parsed
        parenthesis_closed = False
        stack = list()
        while not is_EOF(idx, parsed) and not parenthesis_closed:
            elem = parsed[idx]
            idx = self.__parse_elem(elem, idx, stack)
            if not is_EOF(idx, parsed):
                parenthesis_closed = parsed[idx].type == TokenType.CP
        if not parenthesis_closed:
            raise WrongSyntaxException("Скобки остались открытыми")

        if len(stack) == 1:
            return stack.pop(), idx + 1
        else:
            raise WrongSyntaxException("Ошибка при парсинге скобок")

    def __parse_operator(self, elem, idx, stack):
        """
        :param idx: индекс следующего за оператором элемента
        :param stack: текущий стек
        :return: нода, определяющая операцию выполняемую с оператором
        """
        if len(stack) == 0:
            raise WrongSyntaxException("Оператор не может быть первым символом")
        left = stack.pop()
        if elem.value == "AND":
            local_stack = list()
            idx = self.__parse_elem(self.parsed[idx], idx, local_stack)
            right = local_stack.pop()
            stack.append(AndNode(left, right))
            return idx
        elif elem.value == "OR":
            parsed = self.parsed
            local_stack = list()
            while not is_EOF(idx, parsed) and parsed[idx].value != "OR":
                local_elem = parsed[idx]
                if local_elem.type == TokenType.CP:
                    if not local_stack:
                        raise exceptions.WrongSyntaxException("Неправильное положение закрывающей скобки")
                    else:
                        break
                idx = self.__parse_elem(local_elem, idx, local_stack)
            right = local_stack.pop()
            stack.append(OrNode(left, right))
            return idx
        else:
            raise WrongSyntaxException("Неизвестный оператор")
# (олег OR петр) AND Димон AND Сема
# олег OR )

