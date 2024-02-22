from tokens import TokenType, Token
import exceptions
from tree_nodes import TreeNode, NotNode, AndNode, OrNode, LexemeNode


class TreeBuilder:
    parsed: list[Token]

    def __init__(self, parsed: list[Token]):
        self.parsed = parsed

    def build(self) -> TreeNode:
        return self.__parse_expression(0)

    # end_idx - следующий символ после последнего, вошедшего в выражение
    # По идее надо сделать чтобы он парсил до следующего оператора, а не до конца строки
    def __parse_expression(self, idx):
        parsed = self.parsed
        tree_stack = list()
        while idx < len(parsed):
            elem = parsed[idx]
            if elem.type == TokenType.UNARY_OPERATOR:
                idx = self.__process_unary_operator(idx, tree_stack)
            elif elem.type == TokenType.OP:
                idx = self.__process_parenthesis(idx, tree_stack)
            elif elem.type == TokenType.LEXEME:
                self.__process_lexeme(elem, tree_stack)
                idx += 1
            elif elem.type == TokenType.OPERATOR:
                idx = self.__process_operator(elem, tree_stack, idx)
            else:
                raise exceptions.WrongSyntaxException()

        result = self.__get_result(tree_stack)
        if result is None:
            raise exceptions.WrongSyntaxException()

        return result

    def __process_unary_operator(self, idx, tree_stack):
        # Parse Expression будет парсить до конца строки, а не до конца выражения. Конец выражения - следующий оператор
        expression_node, end_idx = self.__parse_expression(idx + 1)
        unary_node = NotNode(expression_node)
        top_elem = None
        if len(tree_stack) != 0:
            top_elem = tree_stack.pop()

        if top_elem is None:
            tree_stack.append(unary_node)
        elif self.__is_operator_node(top_elem) and top_elem.right is None:
            top_elem.right = unary_node
        else:
            raise exceptions.WrongSyntaxException()
        return end_idx

    def __process_parenthesis(self, idx, tree_stack):
        if idx == len(self.parsed) - 1 or self.parsed[idx + 1].type == TokenType.CP:
            raise exceptions.WrongSyntaxException()
        expression_node, end_idx = self.__parse_parenthesis_expression(idx + 1)
        tree_stack.append(expression_node)
        return end_idx

    def __parse_parenthesis_expression(self, idx):
        parsed = self.parsed
        tree_stack = list()
        while idx < len(parsed):
            elem = parsed[idx]
            if elem.type == TokenType.UNARY_OPERATOR:
                idx = self.__process_unary_operator(idx, tree_stack)
            elif elem.type == TokenType.OP:
                idx = self.__process_parenthesis(idx, tree_stack)
            elif elem.type == TokenType.CP:
                result = self.__get_result(tree_stack)
                if result is None:
                    raise exceptions.WrongSyntaxException()
                return result
            elif elem.type == TokenType.LEXEME:
                self.__process_lexeme(elem, tree_stack)
                idx += 1
            elif elem.type == TokenType.OPERATOR:
                self.__process_operator(elem, tree_stack)
            else:
                raise exceptions.WrongSyntaxException()

    def __process_lexeme(self, elem, tree_stack):
        top_elem = None
        if len(tree_stack) != 0:
            top_elem = tree_stack.pop()

        if top_elem is None:
            tree_stack.append(LexemeNode(elem.value))
        elif self.__is_operator_node(top_elem) and top_elem.right is None:
            top_elem.right = LexemeNode(elem.value)
            tree_stack.append(top_elem)
        else:
            raise exceptions.WrongSyntaxException()

    def __process_operator(self, elem, tree_stack, idx):
        top_elem = None
        if len(tree_stack) != 0:
            top_elem = tree_stack.pop()
        if top_elem is None:
            raise exceptions.WrongSyntaxException()
        if elem.value == "AND":
            tree_stack.append(AndNode(top_elem, None))
            return idx + 1
        elif elem.value == "OR":
            right_node, idx = self.__process_or_operator(idx + 1)
            tree_stack.append(OrNode(top_elem, right_node))
            return idx
        else:
            raise exceptions.WrongSyntaxException()

    def __process_or_operator(self, idx):
        parsed = self.parsed
        tree_stack = list()
        while idx < len(parsed):
            elem = parsed[idx]
            if elem.type == TokenType.UNARY_OPERATOR:
                idx = self.__process_unary_operator(idx, tree_stack)
            elif elem.type == TokenType.OP:
                idx = self.__process_parenthesis(idx, tree_stack)
            elif elem.type == TokenType.LEXEME:
                self.__process_lexeme(elem, tree_stack)
                idx += 1
            elif elem.type == TokenType.OPERATOR:
                if elem.value == "OR":
                    return tree_stack.pop(), idx
                elif elem.value == "AND":
                    tree_stack.append(AndNode(tree_stack.pop(), None))
                else:
                    raise exceptions.WrongSyntaxException()
            else:
                raise exceptions.WrongSyntaxException()

        result = self.__get_result(tree_stack)
        if result is None:
            raise exceptions.WrongSyntaxException()

        return result


    def __is_operator_node(self, top_elem):
        return isinstance(top_elem, (AndNode, OrNode))

    def __get_result(self, tree_stack):
        top_elem = None
        if len(tree_stack) != 0:
            top_elem = tree_stack.pop()

        if isinstance(top_elem, (LexemeNode, NotNode)):
            return top_elem
        if (self.__is_operator_node(top_elem)
                and top_elem.right is not None
                and top_elem.left is not None):
            return top_elem
