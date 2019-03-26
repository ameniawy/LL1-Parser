
import argparse
from collections import OrderedDict


def read_grammar(file_name):
    grammar = dict()
    first = dict()
    follow = dict()
    start_var = ''
    with open(file_name, "r") as file:
        counter = 0
        for line in file.readlines():
            rule_id, operands, first_list, follow_list = line.split(':')
            operands = [operand.strip().split()
                        for operand in operands.strip().split("|")]
            first_list = first_list.split()
            follow_list = follow_list.split()

            grammar[rule_id.strip()] = operands
            first[rule_id.strip()] = first_list
            follow[rule_id.strip()] = follow_list
            if counter == 0:
                start_var = rule_id

            counter += 1

    return grammar, first, follow, start_var


def read_input_string(file_name):
    with open(file_name, "r") as file:
        input_string = file.readline().strip().split()

        return input_string


def get_productions(grammar, first, rule_id, terminal):
    res = []
    for production in grammar[rule_id]:
        for literal in production:
            # if literal is directly terminal or if terminal is in first of that variable
            if literal == terminal or (literal in grammar and terminal in first[literal]):
                res.append(production)
                break
            if literal in grammar and 'epsilon' not in first[literal]:
                break

            if literal not in grammar and literal != terminal:
                break

    return res


def get_terminals(grammar):
    terminals = set()
    terminals.add('$')
    for _, productions in grammar.items():
        for production in productions:
            for literal in production:
                if literal.strip() not in grammar.keys() and literal.strip() != 'epsilon':
                    terminals.add(literal.strip())

    return list(terminals)


def compute_LL1_table(grammar, first, follow):
    terminals = get_terminals(grammar)

    if 'epsilon' in terminals:
        terminals.remove('epsilon')

    table = OrderedDict()

    for key in grammar:
        for terminal in terminals:
            table[(key, terminal)] = []

    for rule_id in grammar.keys():
        for first_literal in first[rule_id]:
            productions = get_productions(
                grammar, first, rule_id, first_literal)

            if first_literal == 'epsilon':
                for follow_literal in follow[rule_id]:
                    table[(rule_id, follow_literal)] = [productions[0]]

            else:
                if len(productions) > 1:
                    return None
                table[(rule_id, first_literal)] = [productions[0]]

    return table


def check_input(input_string, table, grammar, start_variable, first, follow):
    terminals = get_terminals(grammar)

    input_string.append('$')

    stack = list()
    stack.append('$')
    stack.append(start_variable)

    while(len(stack) > 0):
        string_literal = input_string[0].strip()
        stack_literal = stack.pop().strip()

        if string_literal not in grammar and string_literal not in terminals:
            return False

        # case 1: terminal and terminal
        if string_literal not in grammar and stack_literal not in grammar:
            input_string = input_string[1:]
            pass

        # case 2: term, var
        elif string_literal not in grammar and stack_literal in grammar:
            next_rule = table[(stack_literal, string_literal)]
            if len(next_rule) != 1:
                return False

            if next_rule[0] == ['epsilon']:
                continue

            for literal in reversed(next_rule[0]):
                stack.append(literal)

        # case 3: $, var
        elif string_literal == '$' and stack_literal in grammar:
            next_rule = table[(stack_literal, string_literal)]
            if len(next_rule) != 1:
                return False

            if next_rule[0] == ['epsilon']:
                continue

            for literal in reversed(next_rule[0]):
                stack.append(literal)

        # case 4: $, term
        elif string_literal == '$' and stack_literal not in grammar:
            return False

        # case 5: term, $
        elif string_literal not in grammar and string_literal != '$' and stack_literal == '$':
            return False

        # case 6, $, $
        elif string_literal == '$' and stack_literal == '$':
            return True

    return True


def output_fail(file_name):
    output_file = open(file_name, 'w+')
    output_file.write('invalid LL(1) grammar')


def output_parsing_table(file_name, table):
    output_file = open(file_name, 'w+')
    for (rule, terminal) in table.keys():
        goto_list = table[(rule, terminal)]
        if len(goto_list) > 0:
            goto_list = goto_list[0]
        line = rule + ' : ' + terminal + ' : ' + ' '.join(goto_list) + '\n'
        output_file.write(line)


def output_string_check(file_name, valid):
    output_file_2 = open(file_name, 'w+')
    output_file_2.write('yes' if valid else 'no')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        add_help=True, description='Sample Commandline')

    parser.add_argument('--grammar', action="store",
                        help="path of file to take as input to read grammar", nargs="?", metavar="dfa_file")
    parser.add_argument('--input', action="store",
                        help="path of file to take as input to test strings on LL table", nargs="?", metavar="input_file")

    args = parser.parse_args()

    output_file_1 = 'task_6_1_result.txt'
    output_file_2 = 'task_6_2_result.txt'

    # read grammar, first, follow, start variable
    grammar, first, follow, start_variable = read_grammar(args.grammar)
    # read input string
    input_string = read_input_string(args.input)

    # compute parsing table
    table = compute_LL1_table(grammar, first, follow)

    if table:
        # output parsing table
        output_parsing_table(output_file_1, table)
        # check input string against table
        valid = check_input(input_string, table, grammar,
                            start_variable, first, follow)
        # ourput string check result
        output_string_check(output_file_2, valid)

    else:
        output_fail(output_file_1)
