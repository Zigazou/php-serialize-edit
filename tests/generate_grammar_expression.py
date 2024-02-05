#!/usr/bin/env python3
from random import choice

OR = -1
AND = -2
MANY = -3
MAYBE = -4

COMMAND = 0
GET = 1
SET = 2
DELETE = 3
SELECTOR = 4
NOTHING = 5
VALUE = 6
INDEX = 7
NUMBER = 8
STRING = 9
ARRAY = 10
BOOL = 11
NULL = 12
KEY_VALUE = 13
DIGIT = 14
CHAR = 15

GRAMMAR = {
    COMMAND: [OR, GET, SET, DELETE],
    GET: [AND, "G:", [OR, SELECTOR, NOTHING]],
    SET: [AND, "S:", [OR, SELECTOR, NOTHING], "=", VALUE],
    DELETE: [AND, "D:", SELECTOR],
    SELECTOR: [OR, INDEX, [AND, INDEX, '/', SELECTOR]],
    INDEX: [OR, NUMBER, STRING],
    VALUE: [OR, NUMBER, STRING, ARRAY, BOOL, NULL],
    ARRAY: [AND, '[', KEY_VALUE, [MANY, [AND, ',', KEY_VALUE]], ']'],
    KEY_VALUE: [AND, VALUE, ':', VALUE],
    NUMBER: [AND, [MAYBE, '-'], DIGIT, [MANY, DIGIT], [MAYBE, [AND, '.', [MANY, DIGIT]]]],
    STRING: [AND, '"', CHAR, [MANY, CHAR], '"'],
    BOOL: [OR, 'true', 'false'],
    NULL: 'null',
    NOTHING: '',
    DIGIT: [OR, '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    CHAR: [OR,
           ' ', '0', '@', 'P', '`', 'p',
           '!', '1', 'A', 'Q', 'a', 'q',
           '\\"', '2', 'B', 'R', 'b', 'r',
           '#', '3', 'C', 'S', 'c', 's',
           '$', '4', 'D', 'T', 'd', 't',
           '%', '5', 'E', 'U', 'e', 'u',
           '&', '6', 'F', 'V', 'f', 'v',
           "'", '7', 'G', 'W', 'g', 'w',
           '(', '8', 'H', 'X', 'h', 'x',
           ')', '9', 'I', 'Y', 'i', 'y',
           '*', ':', 'J', 'Z', 'j', 'z',
           '+', ';', 'K', '[', 'k', '{',
           ',', '<', 'L', '\\\\', 'l', '|',
           '-', '=', 'M', ']', 'm', '}',
           '.', '>', 'N', '^', 'n', '~',
           '/', '?', 'O', '_', 'o',]
}

def make_mistake(items: str) -> str:
    global mistake_done
    mistake_type = choice(range(6))
    
    if mistake_type == 0:
        return items
    
    if mistake_type == 1:
        return items[1:]

    if mistake_type == 2:
        return items[:-1]

    if mistake_type == 3:
        return items + ' '
    
    if mistake_type == 4:
        return ' ' + items

    if mistake_type == 5:
        return 'x'
    
    return items

VALID = True

def use_values(items):
    if isinstance(items, str):
        if VALID:
            return items
        else:
            return make_mistake(items)

    if isinstance(items, int):
        return generate_expression(items)

    if isinstance(items, list):
        operator = items[0]
        values = items[1:]

        if operator == OR:
            return use_values(choice(values))

        if operator == AND:
            return "".join([use_values(value) for value in values])

        if operator == MANY:
            count = choice(range(0, 15))
            if count != 0:
                return "".join([use_values(values[0]) for _ in range(count)])
            else:
                return ''

        if operator == MAYBE:
            maybe = choice([True, False])
            if maybe:
                return use_values(values[0])
            else:
                return ''

    raise ValueError("Should not happen!: " + str(items))


def generate_expression(start=COMMAND):
    return use_values(GRAMMAR[start])


def main():
    global VALID
    examples = set()
    VALID = True
    for _ in range(100):
        try:
            generated = generate_expression()
            examples.add(bytes(generated, 'ascii'))
        except RecursionError:
            pass

    print('    @parameterized.expand([')
    for example in examples:
        print(f'        ["valid", {example}],')

    print('    ])')
    print('    def test_valid(self, _name, expression):')
    print('        try:')
    print('            Query([]).run(expression)')
    print('        except ParseError as e:')
    print("            raise AssertionError(f'Error on {expression}: {e}')")

    examples = set()
    VALID = False
    for _ in range(100):
        try:
            generated = generate_expression()
            examples.add(bytes(generated, 'ascii'))
        except RecursionError:
            pass

    print('    @parameterized.expand([')
    for example in examples:
        print(f'        ["invalid", {example}],')

    print('    ])')
    print('    def test_invalid(self, _name, expression):')
    print('        with self.assertRaises(ParseError):')
    print('            Query([]).run(expression)')


if __name__ == '__main__':
    main()
