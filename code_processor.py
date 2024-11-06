from abc import ABC, abstractmethod
import re

class CodeProcessor:
    def __init__(self):
        self.factory = StatementFactory()
        self.validator_chain = CodeBeginValidator(CodeBlockValidator(CodeInBlockStatementValidator(CodeFunctionScopeValidator(CodeCallFunctionMatchValidator(CodeNamingCheckValidator(CodeValueCheckValidator(CodeTypeCheckValidator(CodeEndValidator(None)))))))))
        self.optimizers = [CodeUnusedOptimizer(),CodeRepeatDefinedOptimizer(),CodeUnreachableOptimizer()]
        self.organizer = CodeOrganizer()
        self.executor = CodeExecutor()
        self.closed_block_match = {}
        self.reverse_closed_block_match = {}
        self.in_block_keywords = {}
        self.function_scope = {}
        self.call_function_match = {}
        self.call_stack = {}
        self.body = []
        self.index = 0
    def validator_notify(self,message):
        return self.validator_chain.update(self, message)
    def optimizer_notify(self, message):
        for optimizer in self.optimizers:
            optimizer.update(self, message)
        self.organizer.update(self, message)
    def append_code(self, statement_type, *args, **kwargs):
        statement = self.factory.create_statement(statement_type, *args, **kwargs)
        self.body.append(statement)
        statement.mkindex(self.index)
        self.index += 1
    def execute(self):
        self.invalid = [False] * self.index
        signal, response = self.validator_notify("Start Checking")
        if signal == "stop":
            print(response)
        self.optimizer_notify("Start Optimizing")
        self.executor.execute(self)

class Statement(ABC):
    def __init__(self):
        self.index = None
    def mkindex(self, index):
        self.index=index

class StatementFactory:
    def create_statement(self, statement_type, *args, **kwargs):
        statement_classes = {"define":Definition, "operate":Operation, "if":If, "elif":Elif, "else":Else, "condition-end":ConditionEnd, "switch":Switch, "case":Case, "default":Default, "switch-end":SwitchEnd, "for":For, "while":While, "loop-end":LoopEnd, "continue":Continue, "break":Break, "function":Function, "call":Call, "return":Return, "function-end":FunctionEnd, "try":Try, "throw":Throw, "catch":Catch, "exception-end":ExceptionEnd, "print":Print, "scan":Scan}
        if statement_type not in statement_classes:
            raise ValueError("Error: Undefined statement type")
        return statement_classes[statement_type](*args, **kwargs)

class Definition(Statement):
    def __init__(self, variable, variable_type, value):
        self.type = "define"
        self.variable = variable
        self.variable_type = variable_type
        self.value = value
class Operation(Statement):
    def __init__(self, variable, variable_type, operate, *values):
        self.type = "operate"
        self.variable = variable
        self.variable_type = variable_type
        self.operate = operate
        self.values = values
class If(Statement):
    def __init__(self, condition):
        self.type = "if"
        self.condition = condition
class Elif(Statement):
    def __init__(self, condition):
        self.type = "elif"
        self.condition = condition
class Else(Statement):
    def __init__(self):
        self.type = "else"
class ConditionEnd(Statement):
    def __init__(self):
        self.type = "condition-end"
class Switch(Statement):
    def __init__(self, variable):
        self.type = "switch"
        self.variable = variable
class Case(Statement):
    def __init__(self,variable, value):
        self.type = "case"
        self.variable = variable
        self.value = value
class Default(Statement):
    def __init__(self):
        self.type = "default"
class SwitchEnd(Statement):
    def __init__(self):
        self.type = "switch-end"
class For(Statement):
    def __init__(self, operate, condition, *initial):
        self.type = "for"
        self.condition = condition
        self.initial = initial
        self.operate = operate
        self.temp_store_list = []
        self.non_temp_store_list = []
        self.has_out = False
    def temp_store(self, processor):
        for i in self.initial:
            if not processor.body[processor.in_block_keywords[self.index]].show_variable(i["name"]):
                self.temp_store_list.append(i)
                processor.body[processor.in_block_keywords[self.index]].define_variable(i["name"],i["value"])
                continue
            self.non_temp_store_list.append(i)
    def recover_initial(self, processor):
        for i in self.initial:
            if i in self.temp_store_list:
                processor.body[processor.in_block_keywords[self.index]].remove_variable(i["name"])
                continue
            processor.body[processor.in_block_keywords[self.index]].define_variable(i["name"],i["value"])
class While(Statement):
    def __init__(self, condition):
        self.type = "while"
        self.condition = condition
class LoopEnd(Statement):
    def __init__(self):
        self.type = "loop-end"
        self.loop_else = False
    def set_loop_else(self):
        self.loop_else = True
class Continue(Statement):
    def __init__(self):
        self.type = "continue"
class Break(Statement):
    def __init__(self):
        self.type = "break"
class Function(Statement):
    def __init__(self, function_name, return_value_type, *format_arguments):
        self.type = "function"
        self.function_name = function_name
        self.return_value_type = return_value_type
        self.format_arguments = format_arguments
        self._local_scope = {}
    def give_return_value_type(self):
        return self.return_value_type
    def give_format_arguments_data(self):
        return self.format_arguments
    def define_variable(self,variable,value):
        self._local_scope[variable] = value
    def show_variable(self, name):
        return name in self._local_scope
    def get_variable(self,variable):
        return self._local_scope[variable]
    def remove_variable(self,variable):
        return self._local_scope.pop(variable)
class Call(Statement):
    def __init__(self, function_name, variable = None, *actual_arguments):
        self.type = "call"
        self.function_name = function_name
        self.actual_arguments = actual_arguments
        self.variable = variable
        self._has_return = False
        self._return_value = None
    def set_has_return(self):
        self._has_return = True
    def get_return_value(self, return_value):
        self._return_value = return_value
class Return(Statement):
    def __init__(self, return_value): 
        self.type = "return"
        self.return_value = return_value
class FunctionEnd(Statement):
    def __init__(self):
        self.type = "function-end"
class Try(Statement):
    def __init__(self):
        self.type = "try"
class Throw(Statement):
    def __init__(self, exception):
        self.type = "throw"
        self.exception = exception
class Catch(Statement):
    def __init__(self):
        self.type = "catch"
        self.exception = None
    def set_exception(self,exception):
        self.exception = exception
class Finally(Statement):
    def __init__(self):
        self.type = "finally"
class ExceptionEnd(Statement):
    def __init__(self):
        self.type = "exception-end"
class Print(Statement):
    def __init__(self, value):
        self.type = "print"
        self.value = value
class Scan(Statement):
    def __init__(self, variable):
        self.type = "scan"
        self.variable = variable

class CodeValidator(ABC):
    def __init__(self, success_validator):
        self._success_validator = success_validator
    @abstractmethod
    def update(self, processor, message):
        self.processor = processor
        self.message = message
    def next(self):
        if self._success_validator:
            return self._success_validator.update(self.processor, self.message)
        return "continue", None

class CodeBeginValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Begin Validator Received Update: {message}")
        return self.next()

class CodeBlockValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Block Validator Received Update: {message}")
        brace_stack = []
        valid_past_types = {"elif":{"if", "elif"}, "else":{"if", "elif"}, "catch":{"try"}, "finally":{"catch"}, "case":{"switch"}, "default":{"case"},"condition-end":{"if", "elif", "else"}, "loop-end":{"for":"while"}, "function-end":{"function"}, "exteption-end":{"catch", "finally"}}
        for line in processor.body:
            if line.type in {"if", "for", "while", "switch", "function", "try"}:
                brace_stack.append(line)
            elif line.type in {"elif", "else", "catch", "finally", "case", "default","condition-end" , "loop-end", "function-end", "exception-end"}:
                if len(brace_stack) == 0:
                    return "stop", f"Error: Unmatched brace\nLine: {line.index}"
                elif brace_stack[-1] not in valid_past_types[line.type]:
                    return "stop", f"Error: Unmatched brace\nLine: {line.index}"
                processor.closed_block_match[brace_stack.pop().index] = line.index
                if line.type in {"elif", "else", "catch", "finally", "case", "default"}:
                    brace_stack.append(line)
        if len(brace_stack) != 0:
            return "stop", f"Error: Unmatched brace\nLine: {brace_stack[-1].index}"
        return self.next()

class CodeInBlockStatementValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code In-block Statement Validator Received Update: {message}")
        valid_types = {"continue":{"for","while"},"break":{"for", "while", "switch"},"throw":{"try"},"return":{"function"}}
        for line in processor.body:
            for block_line in processor.body[:line.index]:
                if line.type in valid_types and block_line.type in valid_types[line.type] and processor.closed_block_match[block_line.index, -1] > line.index:
                    processor.in_block_keywords[line.index] = block_line.index
                    break
            if line.index not in processor.in_block_keywords:
                return "stop",f"Error: Invalid in-block keyword\nLine: {line.index}"
        return self.next()

class CodeFunctionScopeValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Function Scope Validator Received Update: {message}")
        in_function_scope = {}
        for line in processor.body:
            for function_line in processor.body[:line.index]:
                if function_line.type == "function" and processor.closed_block_match[function_line.index] > line.index:
                    in_function_scope[line.index] = function_line.index
        processor.function_scope = {}
        for key, value in processor.function_scope:
            if value not in processor.function_scope:
                processor.function_scope[value] = []
            else:
                processor.function_scope[value].append(key)
        return self.next()

class CodeCallFunctionMatchValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Call Function Match Validator Received Update: {message}")
        for line in [line for line in processor.body if line.type == "call"]:
            for function_index, scope in processor.function_scope.items():
                if line.index in scope:
                    for local_line_index in [local_line_index for local_line_index in scope if processor.body[local_line_index].type == "function"]:
                        if processor.body[local_line_index].function_name == line.function_name:
                            processor.call_function_match[line.index] = local_line_index
                    if line.index not in processor.call_function_match and processor.body[function_index].function_name == line.function_name:
                        processor.call_function_match[line.index] = function_index
            if line.index not in processor.call_function_match:
                for function_index in [function_index for function_index in processor.function_scope.key() if all(function_index not in [other_scope for other_function_index, other_scope in processor.function_scope.items() if function_index != other_function_index])]:
                    if processor.body[function_index].function_name == line.function_name:
                        processor.call_function_match[line.index] = function_index
        return self.next()

class CodeNamingCheckValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Naming Check Validator Received Update: {message}")
        pat = r"^[A-Za-z_][A-Za-z0-9_]*$"
        for line in processor.body:
            if line.type in {"define", "operate", "scan"}:
                if line.variable is None:
                    return "stop", f"Error: Variables should be named\nLine: {line.index}"
                elif re.match(pat,line.variable) is None:
                    return "stop",f"Error: Illegal naming\nLine: {line.index}"
            elif line.type == "function":
                if line.function_name is None:
                    return "stop", f"Error: Function should be named\nLine: {line.index}"
                elif re.match(pat, line.function_name) is None:
                    return "stop",f"Error: Illegal naming\nLine: {line.index}"
                for argument in line.format_arguments:
                    if re.match(pat, argument["name"]) is None:
                        return "stop",f"Error: Illegal naming\nLine: {line.index}"
            elif line.type == "call":
                if re.match(pat, line.function_name) is None:
                    return "stop",f"Error: Illegal naming\nLine: {line.index}"
                if line.variable is None:
                    pass
                elif re.match(pat,line.variable) is None:
                    return "stop",f"Error: Illegal naming\nLine: {line.index}"
        return self.next()

class CodeValueCheckValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Value Check Validator Received Update: {message}")
        for line in processor.body:
            if line.type in {"define", "print"}:
                if processor.body[processor.in_block_keywords[line.index]].show_variable(line.value):
                    line.value = processor.body[processor.in_block_keywords[line.index]].get_variable(line.value)
            elif line.type == "operate":
                for i, value in enumerate(line.values):
                    if processor.body[processor.in_block_keywords[line.index]].show_variable(value):
                        line.values[i] = processor.body[processor.in_block_keywords[line.index]].get_variable(value)
            elif line.type == "call":
                for i, argument in enumerate(line.actual_arguments):
                    if processor.body[processor.in_block_keywords[line.index]].show_variable(argument):
                        line.actual_arguments[i] = processor.body[processor.in_block_keywords[line.index]].get_variable(argument)
        return self.next()

class CodeTypeCheckValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code Type Check Validator Received Update: {message}")
        for line in processor.body:
            if line.type in {"define", "operate"}:
                if line.variable_type is None:
                    return "stop", f"Error: Variables have no type\nLine: {line.index}"
                elif line.type == "define" and not isinstance(line.value, line.variable_type):
                    return "stop", f"Error: Variable type mismatch\nLine: {line.index}"
                elif line.type == "operate" and not isinstance(line.operate(*line.values), line.variable_type):
                    return "stop", f"Error: Variable type mismatch\nLine: {line.index}"
            elif line.type == "call":
                format_arguments = processor.body[processor.call_function_match[line.index]].give_format_arguments_data()
                if len(line.actual_arguments) < len(format_arguments):
                    return "stop", f"Error: Missing required arguments\nLine: {line.index}"
                elif len(line.actual_arguments) > len(format_arguments):
                    return "stop", f"Error: Passing in extra arguments\nLine: {line.index}"
                for i, argument in enumerate(format_arguments):
                    if not isinstance(line.actual_arguments[i], argument["type"]):
                        return "stop", f"Error: Argument type mismatch\nLine: {line.index}"
                if (line.variable is None and line.variable_type is not None) or (line.variable is not None and line.variable is None):
                    return "stop", f"Error: Unclear attitude\nLine: {line.index}"
                elif line.variable is not None and line.variable_type is not None and not isinstance(line.return_value, line.variable_type):
                    return "stop", f"Error: Return value type mismatch\nLine: {line.index}"
            elif line.type == "return":
                return_value_type = processor.body[processor.in_block_keywords[line.index]].give_return_value_type()
                if not isinstance(line.return_value, return_value_type):
                    return "stop", f"Error: Return value type mismatch\nLine: {line.index}"
        return self.next()

class CodeEndValidator(CodeValidator):
    def update(self, processor, message):
        super().update(processor, message)
        print(f"Code End Validator Received Update: {message}")
        return self.next()

class CodeOptimizer(ABC):
    @abstractmethod
    def update(self, processor, message):
        self.processor = processor
        self.message = message

class CodeUnusedOptimizer(CodeOptimizer):
    def update(self, processor, message):
        print(f"Code Unused Optimizer Received Update: {message}")
        for function_index, end_index in {index:end_index for index, end_index in processor.closed_block_match.items() if processor.body[index].type == "function"}.items():
            if function_index not in [function_index for function_index in processor.function_scope.key() if all(function_index not in [other_scope for other_function_index, other_scope in processor.function_scope.items() if function_index != other_function_index])]:
                if all(processor.body[function_index].function_name != processor.body[call_index].function_name and call_index for call_index in [in_scope_line_index for in_scope_line_index in [scope for scope in processor.function_scope.values() if function_index in scope][0] if processor.body[in_scope_line_index].type == "call"]):
                    for i in range(function_index, end_index + 1):
                        processor.invalid[i] = True
            else:
                if all(call_line.function_name != processor.body[function_index].index and call_line for call_line in processor.body if all(call_line not in [scope for scope in processor.function_scope.values()]) and call_line.type == "call"):
                    for i in range(function_index, end_index + 1):
                        processor.invalid[i] = True

class CodeRepeatDefinedOptimizer(CodeOptimizer):
    def update(self, processor, message):
        print(f"Code Repeat Defined Optimizer Received Update: {message}")
        for function_index, end_index in {index:end_index for index, end_index in processor.closed_block_match.items() if processor.body[index].type == "function"}.items():
            if function_index not in [function_index for function_index in processor.function_scope.key() if all(function_index not in [other_scope for other_function_index, other_scope in processor.function_scope.items() if function_index != other_function_index])]:
                for in_scope_function_index in [in_scope_line_index for in_scope_line_index in [scope for scope in processor.function_scope.values() if function_index in scope][0] if processor.body[in_scope_line_index].type == "function"]:
                    if processor.body[in_scope_function_index].function_name == processor.body[function_index] and in_scope_function_index != function_index:
                        for i in range(function_index, end_index + 1):
                            processor.invalid[i] = True
                        break
            else:
                for in_global_function_index in [function_index for function_index in processor.function_scope.key() if all(function_index not in [other_scope for other_function_index, other_scope in processor.function_scope.items() if function_index != other_function_index])]:
                    if processor.body[in_global_function_index].function_name == processor.body[function_index] and in_global_function_index != function_index:
                        for i in range(function_index, end_index + 1):
                            processor.invalid[i] = True
                        break

class CodeUnreachableOptimizer(CodeOptimizer):
    def update(self, processor, message):
        print(f"Code Unreachable Optimizer Received Update: {message}")
        for line_index, block_index in processor.in_block_keywords.items():
            current_block_end_index = processor.closed_block_match[block_index]
            for internal_block_index in [internal_block_index for internal_block_index in processor.closed_block_match if block_index <= internal_block_index < processor.closed_block_match[block_index]]:
                if internal_block_index < line_index and processor.closed_block_match[internal_block_index] > line_index:
                    current_block_end_index = processor.closed_block_match[internal_block_index]
                elif internal_block_index > line_index:
                    break
            for i in range(line_index + 1, current_block_end_index):
                processor.invalid[i] = True

class CodeOrganizer:
    def update(self, processor, message):
        print(f"Code Organizer Received Update: {message}")
        old_new_match = {}
        processor.body.chear()
        for new_i, line in enumerate([line for old_i, line in enumerate(processor.body) if not processor.invalid[old_i]]):
            old_new_match[line.index] = new_i
            line.mkindex(new_i)
            processor.append(line)
        processor.closed_block_match = {old_new_match[key]:old_new_match[value] for key, value in processor.closed_block_match.items()}
        processor.reverse_closed_block_match = {old_new_match[key]:old_new_match[value] for key, value in processor.reverse_closed_block_match.items()}
        processor.in_block_keywords = {old_new_match[key]:old_new_match[value] for key, value in processor.in_block_keywords.items()}
        processor.function_scope = {old_new_match[key]:old_new_match[value] for key, value in processor.function_scope.items()}
        processor.call_function_match = {old_new_match[key]:old_new_match[value] for key, value in processor.call_function_match.items()}
        processor.call_stack = [old_new_match[value] for value in processor.call_function_match]
        self.next()

class CodeExecutor:
    def execute(self, processor):
        ptr = 0
        while ptr < processor.index:
            line = processor.body[ptr]
            if line.type == "define":
                processor.body[processor.in_block_keywords[line.index]].define_variable(line.variable, line.value)
            elif line.type == "operate":
                processor.body[processor.in_block_keywords[line.index]].define_variable(line.variable, line.operate(*line.values))
            elif line.type in {"if", "elif"} and not line.condition():
                ptr = processor.closed_block_match[line.index]
            elif line.type == "case" and line.variable == line.value:
                ptr = processor.closed_block_match[line.index]
            elif line.type == "for":
                if line.condition(line.initial):
                    line.temp_store(processor)
                    line.initial = line.operate(*line.initial)
                    continue
                line.recover_initial(processor)
                processor.body[processor.closed_block_match[line.index]].set_loop_else()
                ptr = processor.closed_block_match[line.index]
            elif line.type == "while" and not line.condition():
                processor.body[processor.closed_block_match[line.index]].set_loop_else()
                ptr =  processor.closed_block_match[line.index]
            elif line.type == "loop-end" and line.loop_else:
                ptr = processor.reverse_closed_block_match[line.index]
            elif line.type == "continue":
                ptr = processor.in_block_keywords[line.index]
            elif line.type == "break":
                ptr = processor.closed_block_match[processor.in_block_keywords[line.index]]
            elif line.type == "call":
                if line._has_return:
                    processor.call_stack.pop()
                    format_arguments = processor.body[processor.call_function_match[line.index]].give_format_arguments_data()
                    for argument in format_arguments:
                        processor.body[processor.call_function_match[line.index]].remove_variable(argument)
                    if line.variable is not None:
                        processor.body[processor.in_block_keywords[line.index]].define_variable(line.variable, line._return_value)
                    continue
                processor.call_stack.append(line.index)
                format_arguments = processor.body[processor.call_function_match[line.index]].give_format_arguments_data()
                for i, argument in enumerate(format_arguments):
                    processor.body[processor.call_function_match[line.index]].define_variable(argument["name"],line.actual_arguments[i])
                ptr = processor.call_function_match[line.index]
            elif line.type == "return":
                processor.body[processor.call_stack[-1]].get_return_value(line.value)
                processor.body[processor.call_stack[-1]].set_has_return()
                ptr = processor.call_stack[-1]
            elif line.type == "function-end":
                processor.body[processor.call_stack[-1]].set_has_return()
                ptr = processor.call_stack[-1]
            elif line.type == "throw":
                processor.body[processor.closed_block_match[line.index]].set_exception(f"Exception: {line.exception}\nLine: {line.index}")
                ptr = processor.closed_block_match[processor.in_block_keywords[line.index]]
            elif line.type == "catch":
                if line.exception is not None:
                    print(line.exception)
                    continue
                ptr = processor.closed_block_match[line.index]
            elif line.type == "print":
                print(f"Output: {line.value}")
            elif line.type == "scan":
                processor.body[processor.in_block_keywords[line.index]].define_variable(line.variable, input(f"Enter: Assign the value to {line.variable}"))
