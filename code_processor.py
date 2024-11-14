import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str

    def __repr__(self) -> str:
        return f'Token<{self.type}, {self.value}>'

class Lexer:
    def __init__(self) -> None:
        self.token_regex_patterns: List[Tuple[str, str]] = [
            ('whitespace', r'\s+'),
            ('single_line_comment', r'//.*'),
            ('multi_line_comment', r'/\*.*?\*/'),
            ('+', r'\+(?![=\+])'), # arithmetic_operator
            ('-', r'-(?![=-])'), # arithmetic_operator
            ('*', r'\*(?![=\*])'), # arithmetic_operator
            ('/', r'/(?!=)'), # arithmetic_operator
            ('%', r'%(?!=)'), # arithmetic_operator
            ('**', r'\*\*'), # arithmetic_operator
            ('++', r'\+\+'), # arithmetic_operator
            ('--', r'--'), # arithmetic_operator
            ('>', r'>(?!(=|>{1,2}))'), # comparison_operator
            ('<', r'<(?![=<])'), # comparison_operator
            ('>=', r'>='), # comparison_operator
            ('<=', r'<='), # comparison_operator
            ('==', r'==(?!=)'), # comparison_operator
            ('===', r'==='), # comparison_operator
            ('!=', r'!=(?!=)'), # comparison_operator
            ('!==', r'!=='), # comparison_operator
            ('&&', r'&&(?!=)'), # logical_operator
            ('||', r'\|\|(?!=)'), # logical_operator
            ('!', r'!(?!={1,2})'), # logical_operator
            ('??', r'\?\?(?!=)'), # null_coalescing_operator
            ('?.', r'\?\.'), # null_conditional_operator
            ('&', r'&(?=&={0,1})'), # bitwise_operator
            ('|', r'\|(?=\|={0,1})'), # bitwise_operator
            ('^', r'\^'), # bitwise_operator
            ('~', r'~'), # bitwise_operator
            ('<<', r'<<'), # bitwise_operator
            ('>>', r'>>(?!>)'), # bitwise_operator
            ('>>>', r'>>>'), # bitwise_operator
            ('?', r'\?(?!(\?={0,1}|\.))'), # ternary_operator
            (':', r':'), # ternary_operator
            ('=', r'=(?!(={1,2}|>))'), # assignment_operator
            ('+=', r'\+='), # assignment_operator
            ('-=', r'-='), # assignment_operator
            ('*=', r'\*='), # assignment_operator
            ('/=', r'/='), # assignment_operator
            ('%=', r'%='), # assignment_operator
            ('**=', r'\*\*='), # assignment_operator
            ('&&=', r'&&='), # assignment_operator
            ('||=', r'\|\|='), # assignment_operator
            ('??=', r'\?\?='), # assignment_operator
            (',', r','), # comma_operator
            ('=>', r'=>'), # arrow_function_operator
            ('Number', r'((-?(0(\.\d+|[eE][+-]?\d+)|[1-9]\d*(\.\d+|[eE][+-]?\d+)?)|0)'),
            ('String', r'(\'|"|`)([^\1\\]*(\\.[^\1\\]*)*)\1$'),
            ('Boolean', r'true|false'),
            ('Undefined', r'undefined'),
            ('Null', r'null'),
            ('NaN', r'NaN'),
            ('(', r'\('),
            (')', r'\)'),
            ('[', r'\['),
            (']', r'\]'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('break', r'break(?!\w)'),
            ('case', r'case(?!\w)'),
            ('continue', r'continue(?!\w)'),
            ('default', r'default(?!\w)'),
            ('do', r'do(?!\w)'),
            ('if', r'if(?!\w)'),
            ('else', r'else(?!\w)'),
            ('for', r'for(?!\w)'),
            ('in', r'in(?!\w)'),
            ('of', r'of(?!\w)'),
            ('let', r'let(?!\w)'),
            ('return', r'return(?!\w)'),
            ('switch', r'switch(?!\w)'),
            ('var', r'var(?!\w)'),
            ('while', r'while(?!\w)'),
            ('function', r'function(?!\w)'),
            ('const', r'const(?!\w)'),
            ('identifier', r'[a-zA-Z_]\w*'),
            
        ]
        self.last_token_type = None

    def tokenize(self, source_code: str) -> List[Token]:
        token_list: List[Token] = []
        while source_code:
            found_match = False
            for token_type, regex_pattern in self.token_regex_patterns:
                match_result = re.match(regex_pattern, source_code)
                if match_result:
                    found_match = True
                    token_string = match_result.group(0)

                    if token_type not in {'whitespace', 'single_line_comment', 'multi_line_comment'}:
                        token_list.append(Token(token_type, token_string))

                    source_code = source_code[match_result.end():]
                    break
            if not found_match:
                raise ValueError(f"Unexpected character: {source_code[0]}")
        return token_list


    
    def _unescape_string(self, value: str) -> str:
        value = value[1:-1]
        escape_sequences = {
            r'\\': '\\',
            r'\"': '"',
            r"\'": "'",
            r'\n': '\n',
            r'\t': '\t',
            r'\r': '\r',
            r'\b': '\b',
            r'\f': '\f',
        }
        def replace_escape_sequences(match):
            return escape_sequences.get(match.group(0), match.group(0))
        value = re.sub(r'\\[btnfr\"\'\n\t\r\b\f]', replace_escape_sequences, value)
        return value

class ASTNode:
    def __init__(self, type: str, value: str, children: List['ASTNode'] = None) -> None:
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self) -> str:
        return f'ASTNode<{self.type}, {self.value}, {self.children}>'

    def add_child(self, child: 'ASTNode') -> None:
        self.children.append(child)

    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'value': self.value,
            'children': [child.to_dict() for child in self.children]
        }

class Parser:
    def __init__(self) -> None:
        self.grammar_production = {
            'program': ['statement_list'],
            'statement_list': ['statement', 'statement_list'],
            'statement': ['mutually_exclusive'],
            'expression_statement': ['expression', ';'],
            'expression': ['mutually_exclusive'],
            'prefix_expression': ['mutually_exclusive'],
            'increment_prefix_expression': ['++', 'numerical-valued_operated_item'],
            'decrement_prefix_expression': ['--', 'numerical-valued_operated_item'],
            'not_expression': ['!', 'truth-valued_operated_item'],
            'negative_expression': ['-', 'numerical-valued_operated_item'],
            'bitwise_not_expression': ['~', 'numerical-valued_operated_item'],
            'postfix_expression': ['mutually_exclusive'],
            'increment_postfix_expression': ['numerical-valued_operated_item', '++'],
            'decrement_postfix_expression': ['numerical-valued_operated_item', '--'],
            'binary_expression': ['mutually_exclusive'],
            'arithmetic_expression':['mutually_exclusive'],
            'addition_expression': ['numerical-valued_operated_item', '+', 'numerical-valued_operated_item'],
            'subtraction_expression': ['numerical-valued_operated_item', '-', 'numerical-valued_operated_item'],
            'multiplication_expression': ['numerical-valued_operated_item', '*', 'numerical-valued_operated_item'],
            'division_expression': ['numerical-valued_operated_item', '/', 'numerical-valued_operated_item'],
            'modulus_expression': ['numerical-valued_operated_item', '%', 'numerical-valued_operated_item'],
            'exponentiation_expression': ['numerical-valued_operated_item', '**', 'numerical-valued_operated_item'],
            'comparison_expression': ['mutually_exclusive'],
            'greater_than_expression': ['numerical-valued_operated_item', '>', 'numerical-valued_operated_item'],
            'less_than_expression': ['numerical-valued_operated_item', '<', 'numerical-valued_operated_item'],
            'greater_than_or_equal_to_expression': ['numerical-valued_operated_item', '>=', 'numerical-valued_operated_item'],
            'less_than_or_equal_to_expression': ['numerical-valued_operated_item', '<=', 'numerical-valued_operated_item'],
            'equal_to_expression': ['numerical-valued_operated_item', '==', 'numerical-valued_operated_item'],
            'not_equal_to_expression': ['numerical-valued_operated_item', '!=', 'numerical-valued_operated_item'],
            'logical_expression': ['mutually_exclusive'],
            'and_expression': ['truth-valued_operated_item', '&&', 'truth-valued_operated_item'],
            'or_expression': ['truth-valued_operated_item', '||', 'truth-valued_operated_item'],
            'bitwise_expression': ['mutually_exclusive'],
            'bitwise_and_expression': ['numerical-valued_operated_item', '&', 'numerical-valued_operated_item'],
            'bitwise_or_expression': ['numerical-valued_operated_item', '|', 'numerical-valued_operated_item'],
            'bitwise_xor_expression': ['numerical-valued_operated_item', '^', 'numerical-valued_operated_item'],
            'left_shift_expression': ['numerical-valued_operated_item', '<<', 'numerical-valued_operated_item'],
            'right_shift_expression': ['numerical-valued_operated_item', '>>', 'numerical-valued_operated_item'],
            'unsigned_right_shift_expression': ['numerical-valued_operated_item', '>>>', 'numerical-valued_operated_item'],
            'ternary_expression': ['truth-valued_operated_item', '?', 'assigned_operated_item', ':', 'assigned_operated_item'],
            'bracketed_expression': ['(', 'expression', ')'],
            'comma_expression': ['expression', ',', 'expression'],
            'numerical-valued_operated_item': ['mutually_exclusive'], #As a flag, the numerical value of the node will be considered during semantic analysis.
            'truth-valued_operated_item': ['mutually_exclusive'], #As a flag, the truth value of the node will be considered during semantic analysis.
            'assigned_operated_item': ['mutually_exclusive'], #As a flag, the own value of the node will be considered during semantic analysis.
            'variable_declaration_statement': ['variable_declaration', ';'],
            'variable_operation_statement': ['variable_operation', ';'],
            'variable_declaration': ['mutually_exclusive'],
            'global_variable_declaration': ['var', 'variable_operation'],
            'local_variable_declaration': ['let', 'variable_operation'],
            'constant_declaration': ['const', 'variable_operation'],
            'variable_operation': ['identifier', 'assignment_structure'],
            'assignment_structure': ['mutually_exclusive'],
            'basic_assignment_structure': ['=', 'expression'],
            'extended_assignment_structure': ['mutually_exclusive'],
            'addition_assignment_structure': ['+=', 'expression'],
            'subtraction_assignment_structure': ['-=', 'expression'],
            'multiplication_assignment_structure': ['*=', 'expression'],
            'division_assignment_structure': ['/', 'expression'],
            'modulus_assignment_structure': ['%=', 'expression'],
            'exponentiation_assignment_structure': ['**=', 'expression'],
            'and_assignment_structure': ['&&=', 'expression'],
            'or_assignment_structure': ['||=', 'expression'],
            'null_coalescing_assignment_structure': ['??=', 'expression'],
            'if_statement': ['if', '(', 'expression', ')', 'statement_body', 'if_statement_optional_tail'],
            'if_statement_optional_tail': ['mutually_exclusive'],
            'else_if_statement': ['else', 'if', '(', 'expression', ')', 'statement_body', 'else_if_statement_optional_tail'],
            'else_if_statement_optional_tail': ['mutually_exclusive'],
            'else_statement': ['else', 'statement_body'],
            'statement_body': ['{', 'statement_list', '}'],
            'switch_statement': ['switch', '(', 'expression', ')', '{', 'case_list', '}'],
            'case_list': ['mutually_exclusive'],
            'case_statement': ['case', 'expression', ':', 'statement_list', 'optional_case_list_tail'],
            'optional_case_list_tail': ['mutually_exclusive'],
            'default_statement': ['default', ':', 'statement_list'],
            'for_statement': ['for', '(', 'expression', ';', 'expression', ';', 'expression', ')', 'statement_body'],
            'while_statement': ['while', '(', 'expression', ')', 'statement_body'],
            'do_while_statement': ['do', 'statement_body', 'while', '(', 'expression', ')', ';'],
            'function_declaration_statement': ['function', 'identifier', '(', 'formal_parameter_list', ')', 'statement_body'],
            'formal_parameter_list': ['formal_parameter', 'optional_formal_parameter_list_tail'],
            'formal_parameter': ['identifier', 'optional_formal_parameter_tail'],
            'optional_formal_parameter_tail': ['mutually_exclusive'],
            'optional_formal_parameter_list_tail': ['mutually_exclusive'],
            'next_formal_parameter': [',', 'formal_parameter_list'],
            'function_body': ['(', 'formal_parameter_list', ')', '=>', '{', 'statement_list', '}'],
            'function_call_statement': ['function_call', ';'],
            'function_call': ['identifier', '(', 'actual_parameter_list', ')'],
            'actual_parameter_list': ['expression', 'optional_actual_parameter_list_tail'],
            'optional_actual_parameter_list_tail': ['mutually_exclusive'],
            'next_actual_parameter': [',', 'actual_parameter_list'],
            'return_statement': ['return', 'expression', ';'],
            'break_statement': ['break', ';'],
            'continue_statement': ['continue', ';'],
            'for_in_statement': ['for', '(', 'identifier', 'in', 'object_like_item', ')', 'statement_body'],
            'object_like_item': ['mutually_exclusive'],
            'object': ['{', 'object_item_list', '}'],
            'object_item_list': ['object_item', 'optional_object_item_list_tail'],
            'optional_object_item_list_tail': ['mutually_exclusive'],
            'next_object_item': [',', 'object_item_list'],
            'object_item': ['stringifiable_item', ':', 'assigned_operated_item'],
            'stringifiable_item': ['mutually_exclusive'], #As a flag, the stringifiable value of the node will be considered during semantic analysis.
            'array': ['[', 'array_item_list', ']'],
            'array_item_list': ['array_item', 'optional_array_item_list_tail'],
            'optional_array_item_list_tail': ['mutually_exclusive'],
            'next_array_item': [',', 'array_item_list'],
            'array_item': ['assigned_operated_item'],
            'for_of_statement': ['for', '(', 'identifier', 'of', 'iterable_item', ')', 'statement_body'],
            'iterable_item': ['mutually_exclusive'],
        }
        self.mutually_exclusive = {
            'statement': ['expression_statement', 'variable_declaration_statement', 'variable_operation_statement', 'if_statement', 'else_if_statement', 'else_statement', 'switch_statement', 'case_statement', 'defalut_statement', 'for_statement', 'while_statement', 'do_while_statement', 'function_declaration_statement', 'function_call_statement', 'return_statement', 'break_statement', 'continue_statement', 'for_in_statement', 'for_of_statement'],
            'expression': ['assigned_operated_item', 'prefix_expression', 'postfix_expression', 'binary_expression', 'ternary_expression', 'bracketed_expression', 'comma_expression'],
            'prefix_expression': ['increment_prefix_expression', 'decrement_prefix_expression', 'not_expression', 'negative_expression', 'bitwise_not_expression'],
            'postfix_expression': ['increment_postfix_expression', 'decrement_postfix_expression'],
            'binary_expression': ['arithmetic_expression', 'comparison_expression', 'logical_expression', 'bitwise_expression'],
            'arithmetic_expression': ['addition_expression', 'subtraction_expression', 'multiplication_expression', 'division_expression', 'modulus_expression', 'exponentiation_expression'],
            'comparison_expression': ['greater_than_expression', 'less_than_expression', 'greater_than_or_equal_to_expression', 'less_than_or_equal_to_expression', 'equal_to_expression', 'not_equal_to_expression'],
            'logical_expression': ['and_expression', 'or_expression'],
            'bitwite_expression': ['bitwise_and_expression', 'bitwise_or_expression', 'bitwise_xor_expression', 'left_shift_expression', 'right_shift_expression', 'unsigned_right_shift_expression'],
            'numerical-valued_operated_item': ['Number', 'identifier', 'expression'],
            'truth-valued_operated_item': ['Boolean', 'Number', 'String', 'Null', 'Undefined', 'NaN', 'identifier', 'expression'],
            'assigned_operated_item': ['String', 'Number', 'Boolean', 'Null', 'NaN', 'Undefined', 'object', 'array', 'function_body', 'function_call', 'identifier', 'expression'],
            'variable_declaration': ['global_variable_declaration', 'local_variable_declaration', 'constant_declaration'],
            'optional_variable_operation_tail': ['epsilon', 'next_variable_operation'],
            'assignment_structure': ['basic_assignment_structure', 'extended_assignment_structure', 'and_assignment_structure', 'or_assignment_structure', 'null_coalescing_assignment_structure'],
            'extended_assignment_structure': ['addition_assignment_structure', 'subtraction_assignment_structure', 'multiplication_assignment_structure', 'division_assignment_structure', 'modulus_assignment_structure', 'exponentiation_assignment_structure'],
            'if_statement_optional_tail': ['epsilon', 'else_if_statement', 'else_statement'],
            'else_if_statement_optional_tail': ['epsilon', 'else_if_statement', 'else_statement'],
            'case_list': ['case_statement', 'default_statement'],
            'optional_case_list_tail': ['epsilon', 'case_list'],
            'optional_formal_parameter_tail': ['epsilon', 'basic_assignment_structure'],
            'optional_formal_parameter_list': ['epsilon', 'next_formal_parameter'],
            'optional_actual_parameter_list_tail': ['epsilon', 'next_actual_parameter'],
            'object_like_item': ['object', 'array', 'function_body', 'function_call', 'identifier', 'expression'],
            'object_item_list': ['epsilon', 'next_object_item'],
            'stringifiable_item': ['String', 'Number', 'Boolean', 'Null', 'NaN', 'Undefined', 'object', 'array', 'function_body', 'function_call', 'identifier', 'expression'],
            'optional_object_item_list_tail': ['epsilon', 'next_object_item'],
            'array_item_list': ['epsilon', 'next_array_item'],
            'array_item': ['assigned_operated_item'],
            'iterable_item': ['array', 'String', 'function_call', 'identifier', 'expression'],
            'optional_array_item_list_tail': ['epsilon', 'next_array_item'],
            'optional_formal_parameter_list_tail': ['epsilon', 'next_formal_parameter'],
        }
        self.first_set: Dict[str: set[str]] = {}
        self.follow_set: Dict[str: set[str]] = {}
        self.parse_table: Dict[Tuple[str, str], List[str]] = {}
        self._get_first_set()
        self._get_follow_set()
        self._get_parse_table()
    def parse(self, token_list: List[Token]) -> ASTNode:
        stack = ['program']
        root = ASTNode('program', 'program')
        node_stack = [root]
        i = 0
        while stack:
            top = stack.pop()
            current_node = node_stack.pop()
            current_token = token_list[i] if i < len(token_list) else Token('$', '$')
            if top not in self.grammar_production and top == current_token.type:
                current_node.value = current_token.value
                i += 1
                continue
            elif top in self.grammar_production and (top, current_token.type) in self.parse_table:
                production = self.parse_table[(top, current_token.type)]
                print((top, current_token), production)
                for symbol in reversed(production) if isinstance(production, list) else [production]:
                    stack.append(symbol)
                    new_node = ASTNode(symbol, None)
                    current_node.add_child(new_node)
                    node_stack.append(new_node)
            else:
                raise ValueError(f"Unexpected token: {current_token}")
        if i != len(token_list):
            raise ValueError(f"Unexpected token: {token_list[i]}")
        return root     
    def _get_first_set(self) -> None:
        have_change, is_same = False, False
        while not have_change or not is_same:
            for symbol in self.grammar_production:
                first_symbol = self.grammar_production[symbol][0]
                if first_symbol == 'mutually_exclusive':
                    for option in self.mutually_exclusive[symbol]:
                        if option not in self.first_set:
                            self.first_set[option] = set()
                        if option not in self.grammar_production:
                            self.first_set[option] |= {option}
                        if symbol not in self.first_set:
                            self.first_set[symbol] = set()
                        else:
                            self.first_set[symbol] |= self.first_set[option]
                else:
                    if first_symbol not in self.first_set:
                        self.first_set[first_symbol] = set()
                    if first_symbol not in self.grammar_production:
                        self.first_set[first_symbol] |= {first_symbol}
                    if symbol not in self.first_set:
                        self.first_set[symbol] = set()
                    else:
                        self.first_set[symbol] |= self.first_set[first_symbol]
            if not have_change:
                copy_first_set = {k: v.copy() for k, v in self.first_set.items()}
                have_change = True
                continue
            is_same = all(k in copy_first_set and v == copy_first_set[k] for k, v in self.first_set.items())
            if not is_same:
                copy_first_set = {k: v.copy() for k, v in self.first_set.items()}
    def _get_follow_set(self) -> None:
        have_change, is_same = False, False
        while not have_change or not is_same:
            for symbol in self.grammar_production:
                if symbol == 'program':
                    self.follow_set[symbol] = {'$'}
                for non_terminal, production in {k: v for k, v in self.grammar_production.items() if symbol in v}.items():
                    for i in [i for i in range(len(production) - 1) if production[i] == symbol]:
                        if production[i + 1] not in self.first_set:
                            self.first_set[production[i + 1]] = set()
                        if production[i + 1] not in self.grammar_production:
                            self.first_set[production[i + 1]] |= {production[i + 1]}
                        if symbol not in self.follow_set:
                            self.follow_set[symbol] = set()
                        self.follow_set[symbol] |= self.first_set[production[i + 1]] - {'epsilon'}
                        if non_terminal not in self.follow_set:
                            self.follow_set[non_terminal] = set()
                        if 'epsilon' in self.first_set[production[i + 1]] or symbol == production[-1]:
                            self.follow_set[symbol] |= self.follow_set[non_terminal]
                for non_terminal in {k for k, v in self.mutually_exclusive.items() if symbol in v}:
                    if non_terminal not in self.follow_set:
                        self.follow_set[non_terminal] = set()
                    if symbol not in self.follow_set:
                        self.follow_set[symbol] = self.follow_set[non_terminal]
                    else:
                        self.follow_set[symbol] |= self.follow_set[non_terminal]
            if not have_change:
                copy_follow_set = {k: v.copy() for k, v in self.follow_set.items()}
                have_change = True
                continue
            is_same = all(k in copy_follow_set and v == copy_follow_set[k] for k, v in self.follow_set.items())
            if not is_same:
                copy_follow_set = {k: v.copy() for k, v in self.follow_set.items()}
    def _get_parse_table(self) -> Dict[Tuple[str, str], List[str]]:
        for A, alpha in {k: v for k, v in self.grammar_production.items() if v[0] != 'mutually_exclusive'}.items():
            for a in self.first_set[alpha[0]]:
                self.parse_table[(A, a)] = alpha
            if 'epsilon' in self.first_set[alpha[0]]:
                for b in self.follow_set[A]:
                    self.parse_table[(A, b)] = alpha
            if A == 'program':
                for a in {'$'}:
                    self.parse_table[(A, a)] = alpha
        for A, symbols in self.mutually_exclusive.items():
            for symbol in symbols:
                for a in self.first_set[symbol]:
                    self.parse_table[(A, a)] = symbol
                if 'epsilon' in self.first_set[symbol]:
                    for b in self.follow_set[A]:
                        self.parse_table[(A, b)] = symbol