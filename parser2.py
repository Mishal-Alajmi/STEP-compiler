from tokenizer import *


class Node:
    pass


class Statement(Node):
    pass


class Expression(Node):
    pass


class BinaryExpression(Expression):
    def __init__(self, left_exp, operator, right_exp):  # 2 + (3 * 5)
        self.operator = operator
        self.left_exp = left_exp
        self.right_exp = right_exp


class UnaryExpression(Expression):
    def __init__(self, operator, exp):
        self.operator = operator
        self.expression = exp


class LiteralExpression(Expression):
    def __init__(self, exp):
        self.expression = exp


class IdentifierExpression(Expression):
    def __init__(self, exp):
        self.expression = exp


class GroupingExpression(Expression):
    def __init__(self, exp):
        self.expression = exp


class BlockStatement(Node):
    pass


class VarStatement(Statement):
    def __init__(self, token, datatype, identifier, expression):
        self.token = token
        self.datatype = datatype
        self.identifer = identifier
        self.expression = expression


class ConstStatement(Statement):
    def __init__(self, token, datatype, identifier, expression):
        self.token = token
        self.datatype = datatype
        self.identifer = identifier
        self.expression = expression

# print expression


class PrintStatement(Statement):
    def __init__(self, token, expression):
        self.token = token
        self.expression = expression


class WhileStatement(BlockStatement):
    def __init__(self, token, expression, statements=[]):
        self.token = token
        self.expression = expression
        self.statements = statements


class ForStatement(BlockStatement):
    def __init__(self, token, firstExpression, secondExpression, statements=[]):
        self.token = token
        self.firstExpression = firstExpression
        self.seconfExpression = secondExpression
        self.statement = statements


class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = None
        self.next_token = None
        self.current_level = 0

        self.is_first_token = True

    def syntax_error(self, token, message):
        raise Exception('[Step(syntax error)]:' + message + ', ' + token.value +
                        ', line number: ' + str(token.line_number) + ', position: ' + str(token.position))

    def consume(self):

        if self.is_first_token:
            self.current_token = self.tokenizer.tokenize()
            self.is_first_token = False
        else:
            self.current_token = self.next_token

        self.next_token = self.tokenizer.tokenize()

    def print_parser(self):
        # print expression
        return PrintStatement(self.current_token, self.expression())

    def match(self, token_value):
        self.consume()
        if self.current_token.value != token_value:
            self.syntax_error(self.current_token, 'unexpected token')

    def while_parser(self):
        # while expression {statements}
        while_token = self.current_token
        expression = self.expression()
        self.match('{')
        self.current_level += 1
        statements = self.parse()
        # self.match('}')

        return WhileStatement(while_token, expression, statements)

    def for_parser(self):
        # for from_expression to to_expression {statement}
        for_token = self.current_token
        firstExpression = self.expression()
        self.match('to')
        secondExpression = self.expression()
        self.match('{')
        self.current_level += 1
        statements = self.parse()

        return ForStatement(for_token, firstExpression, secondExpression, statements)

    def var_parser(self):
        # var datatype id = expression
        var_token = self.current_token
        self.consume()

        if not self.current_token.category == 'keyword' and not self.current_token.value in ['int', 'float', 'string', 'boolean']:
            self.syntax_error(self.current_token, 'datatype expected')

        datatype_token = self.current_token

        self.consume()
        if self.current_token.category != 'identifier':
            self.syntax_error(self.current_token, 'identifier expected')

        identifier_token = self.current_token
        self.match('=')

        return VarStatement(var_token, datatype_token, identifier_token, self.expression())

    def const_parser(self):
        # const datatype id = expression
        const_token = self.current_token
        self.consume()

        if not self.current_token.category == 'keyword' and not self.current_token.value in ['int', 'float', 'string', 'boolean']:
            self.syntax_error(self.current_token, 'datatype')

        datatype_token = self.current_token

        self.consume()
        if self.current_token.category != 'identifier':
            self.syntax_error(self.current_token, 'Identifer expected')

        identitfier_token = self.current_token
        self.match('=')

        return ConstStatement(const_token, datatype_token, identitfier_token, self.expression())

    def expression(self):
        self.consume()
        expr = self.relational()
        while self.next_token.value == '==' or self.next_token.value == '!=':
            self.consume()
            operator = self.current_token
            self.consume()
            right_expr = self.relational()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def relational(self):
        expr = self.addition()
        while self.next_token.value == '>' or self.next_token.value == '>=' or self.next_token.value == '<' or self.next_token.value == '<=':
            self.consume()
            operator = self.current_token
            self.consume()
            right_expr = self.addition()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def addition(self):  # 2 + 5 * 3
        expr = self.term()
        while self.next_token.value == '+' or self.next_token.value == '-':
            self.consume()
            operator = self.current_token
            self.consume()
            right_expr = self.term()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def term(self):
        expr = self.factor()
        while self.next_token.value == '*' or self.next_token.value == '/':
            self.consume()
            operator = self.current_token
            self.consume()
            right_expr = self.factor()
            expr = BinaryExpression(expr, operator, right_expr)

        return expr

    def factor(self):
        if self.current_token.category == 'literal':
            return LiteralExpression(self.current_token)
        elif self.current_token.category == 'identifier':
            return IdentifierExpression(self.current_token)
        elif self.current_token.value == '(':
            result = GroupingExpression(self.expression())
            self.match(')')
            return result

    def parse(self):
        statements = []
        self.consume()

        while self.current_token.category != 'EOF':

            if self.current_token.category == 'keyword':
                if self.current_token.value == 'var':
                    statements.append(self.var_parser())
                elif self.current_token.value == 'const':
                    statements.append(self.const_parser())
                elif self.current_token.value == 'print':
                    statements.append(self.print_parser())
                elif self.current_token.value == 'while':
                    statements.append(self.while_parser())
                elif self.current_token.value == 'for':
                    statements.append(self.for_parser())

            elif self.current_token.value == '}':
                self.current_level -= 1
                return statements
            elif self.current_token.category == 'comment':
                continue
            elif self.current_token.category == 'whitespace':
                continue
            elif self.current_token.category == 'error':
                self.syntax_error(self.current_token, 'unexpected token')
            else:
                self.syntax_error(self.current_token, 'unexpected token')

            self.consume()

        return statements
