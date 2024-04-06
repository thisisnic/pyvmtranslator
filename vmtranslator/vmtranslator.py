from enum import Enum
import os
import sys

class CommandType(Enum):
    C_ARITHMETIC = 1
    C_PUSH = 2
    C_POP = 3
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9

class Parser:
    def __init__(self, input_file):
        try:
            with open(input_file, 'r') as file:
                file_contents = file.read()
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("An error occurred:", e)

        self.contents = self.clean_contents(file_contents)
        self.next_line_index = 0

    def clean_contents(self, file_contents):
        contents = file_contents.split("\n")
        contents = [line for line in contents if not (line.startswith("//") or line == "")]
        return contents
    
    def parse_next(self):
        line_to_parse = self.contents[self.next_line_index]
        self.next_line_index += 1

        parsed_line = {'og_line': line_to_parse, 'command_type': None, 'arg1': '', 'arg2': ''}
        parsed_line['command_type'] = self.command_type(line_to_parse)
        if(parsed_line['command_type'] != CommandType.C_RETURN):
            parsed_line['arg1'] = self.arg1(line_to_parse, parsed_line['command_type'])
        if(parsed_line['command_type'] in [CommandType.C_PUSH, CommandType.C_POP, CommandType.C_FUNCTION, CommandType.C_CALL]):
            parsed_line['arg2'] = self.arg2(line_to_parse)

        return parsed_line

    def has_more_commands(self):
        return (self.next_line_index < len(self.contents))
        
    def command_type(self, line):
        if line.startswith("push "):
            return CommandType.C_PUSH
        if line.startswith("pop "):
            return CommandType.C_POP
        if self.command_maths(line):
            return CommandType.C_ARITHMETIC
        if line.startswith("call"):
            return CommandType.C_CALL
        if line.startswith("function"):
            return CommandType.C_FUNCTION
        if line.startswith("goto"):
            return CommandType.C_GOTO
        if line.startswith("if-goto"):
            return CommandType.C_IF
        if line.startswith("label"):
            return CommandType.C_LABEL
        else:
            raise ValueError("Unrecognised command type in line: " + line)


    def command_maths(self, line):
        arith_commands = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        return any(line.startswith(command) for command in arith_commands)

    
    def arg1(self, line, command_type):
        if command_type == CommandType.C_ARITHMETIC:
            return line
        else:
            return line.split(" ")[1]
      
    
    def arg2(self, line):
        return line.split(" ")[2]
    

class CodeWriter:
    def __init__(self, output_file):
    # opens the output file/stream and gets it ready to write to
        self.filename = output_file
        self.logical_label_num = 0
        self.static_num = 0
        if os.path.isfile(output_file):
            os.remove(output_file)

    def write_next(self, line):
        try:
            with open(self.filename, 'a') as file:
                file.write(f"//{line['og_line']}\n")
        except Exception as e:
                print("An error occurred while writing to the file:", e)

        if line['command_type'] == CommandType.C_ARITHMETIC:
            self.write_arithmetic(line['arg1'])

        if line['command_type'] in [CommandType.C_PUSH, CommandType.C_POP]:
            self.write_push_pop(line['command_type'], line['arg1'], line['arg2'])

    def write_terminal(self):
        try:
            with open(self.filename, 'a') as file:
                file.write(asm_end_program())
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    def write_arithmetic(self, command):
    # writes to the output file the assembly code that implements
    #  the given arithmetic command
        try:
            with open(self.filename, 'a') as file:
                file.write(self.translate_arithmetic(command))
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    # def asm_load_sp_value(): return "@SP\nA=M-1\nD=M\n"
    # def asm_decrement_address(): return "A=A-1\n"
    # def asm_save_result(args = 1): return "@SP\nA=M\n" + ("A=A-1\n" * args) + "M=D\n"
    # def def asm_decrement_sp():  return "@SP\nM=M-1\n"
                
    def translate_arithmetic(self, arg1):
        if arg1 == "add":
            return asm_load_sp_value() + asm_decrement_address() +"D=D+M\n" + asm_save_result(args = 2) + asm_decrement_sp()
        elif arg1 == "sub":
            return asm_load_sp_value() + asm_decrement_address() + "D=D-M\nD=-D\n"  + asm_save_result(args = 2)+ asm_decrement_sp()
        elif arg1 == "neg":
            return asm_load_sp_value() + "D=-D\n" + asm_save_result(args = 1)
        elif arg1 in ["gt", "lt", "eq"]:
            self.logical_label_num += 1
            return asm_load_sp_value() + asm_decrement_address() + "D=D-M\n" + self.asm_logical_comparison(arg1)
        elif arg1 == "and":
            return asm_load_sp_value() + asm_decrement_address() + "D=D&M\n" + asm_save_result(args = 2)+ asm_decrement_sp()
        elif arg1 == "or":
            return asm_load_sp_value() + asm_decrement_address() + "D=D|M\n" + asm_save_result(args = 2) + asm_decrement_sp()
        elif arg1 == "not":
            return asm_load_sp_value() + asm_decrement_address() + "D=!D\n" + asm_save_result(args = 1) 
        else:  
            return arg1
        

    def asm_logical_comparison(self, op):
        asm_compare_string = ""
        asm_compare_op = ""

        if op == "gt":
            asm_compare_op = "JLT"
        elif op == "lt":
            asm_compare_op = "JGT"
        elif op == "eq":
            asm_compare_op = "JEQ"

        asm_compare_string = "@FALSE" + str(self.logical_label_num) + "\n" + "D;" + asm_compare_op + "\n@SP\nA=M-1\nA=A-1\nM=0\nD=A\n"+asm_decrement_sp()+ \
                            "@CONTINUE" + str(self.logical_label_num) + "\n0;JMP\n"+\
                            "(FALSE" + str(self.logical_label_num) + ")\n@SP\nA=M-1\nA=A-1\nM=-1\nD=A\n"+asm_decrement_sp()+\
                            "(CONTINUE" + str(self.logical_label_num) + ")\n"

        return asm_compare_string

    

    def write_push_pop(self, command, segment, index):
    # `command` is C_PUSH or C_POP, segment is a string, index is an int
    # writes to the output file the assembly code that implements the given command
    #  where command is either C_POP or C_PUSH
        
        string_to_write = str(command) + " " + segment + " " + str(index) + "\n"

        if command == CommandType.C_PUSH and segment == "constant":
            string_to_write = "@" + str(index) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        if segment in ["local", "argument", "this", "that"]:
            string_to_write = asm_push_pop_standard(command, segment, index)
        if segment == "temp":
            string_to_write = asm_push_pop_temp(command, index)
        if segment == "pointer":
            string_to_write = asm_push_pop_pointer(command, index)
        if segment == "static":
            file_name, _ = os.path.splitext(os.path.basename(self.filename))
            string_to_write = asm_static(command, index, file_name)
            
        try:
            with open(self.filename, 'a') as file:
                # put code here to decompose command into commands
                file.write(string_to_write) 
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    
def asm_static(command, index, label_name):
    
    varname = label_name + "." + index
    if command == CommandType.C_POP:
        return f"@SP\nA=M-1\nD=M\n@{varname}\nM=D\n@SP\nM=M-1\n"
    elif command == CommandType.C_PUSH:
        return f"@{varname}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


def get_output_filename(input_filename):
    
    file_name, _ = os.path.splitext(os.path.basename(input_filename))
    output_filename = f"{file_name}.asm"
    
    return os.path.dirname(input_filename) + "/" + output_filename


def asm_push_pop_pointer(command, index):

    index = 3 + int(index)

    # takes the value from the stack and puts it in register and stack decrements
    if command == CommandType.C_POP:
        return f"@SP\nA=M-1\nD=M\n@{index}\nM=D\n@SP\nM=M-1\n"
    # copies the value to stack from register and stack increments
    elif command == CommandType.C_PUSH:
        return f"@{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"

def asm_push_pop_standard(command, segment, index):

    seg = translate_memory_segment(segment)

    # push takes a value from a location and copies it to the stack
    if command == CommandType.C_PUSH:
         
        return f"@{seg}\nD=M\n@{index}\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"  
    
    # pop removes the value from the stack and saves it to the location
    elif command == CommandType.C_POP:
        # get the location and save it in R13                get the value from the prev stack val
        return f"@{seg}\nD=M\n@{index}\nD=D+A\n@13\nM=D\n" + "@SP\nM=M-1\nA=M\nD=M\n@13\nA=M\nM=D\n" 
        
def asm_push_pop_temp(command, index):

    address = 5 + int(index)
    if command == CommandType.C_PUSH:
        # push takes it from temp and puts on the stack   
        return f"@{address}\nD=M\n@SP\nA=M\nM=D\n" + asm_increment_sp()

    elif command == CommandType.C_POP:
        return f"@SP\nA=M-1\nD=M\n@{address}\nM=D\n" + asm_decrement_sp()

def asm_segment_index_from_offset(segment_name, offset):

    """
    Return the asm for getting the RAM location of the relevant segment and storing it in @13 
    Pseudocode: addr=<segment>+<offset>
    
    """

    seg = translate_memory_segment(segment_name)

    return f"@{seg}\nD=M\n@{offset}\nD=D+A\n@13\nM=D\n"

def asm_decrement_sp():
        return "@SP\nM=M-1\n"

def asm_push_to_address_from_sp():
    """
    Return the asm for getting the value from SP and storing it in the value of the address stored in @13
    Pseudocode: *addr=*SP
    """

    return "@SP\nA=M\nD=M\n@13\nA=M\nM=D\n"

def asm_increment_address():
    """
    Increment address A by 1
    """
    return "A=A+1\n"

def asm_decrement_address():
    """
    Decrement address A by 1
    """
    return "A=A-1\n"

def asm_load_sp_value():
    return "@SP\nA=M-1\nD=M\n"

def asm_increment_sp():

    """ 
    Increment SP by 1
    Psedusocode: SP++
    """

    return "@SP\nM=M+1\n"

def asm_decrement_sp():

    """ 
    Decerement SP by 1
    Psedusocode: SP--
    """

    return "@SP\nM=M-1\n"

def asm_save_d_as_m():
    return "M=D\n"

def asm_save_result(args = 1):
	""" args: the number of args the function had """
	return "@SP\nA=M\n" + ("A=A-1\n" * args) + "M=D\n"

def asm_deduct_m_from_d():
        return "D=M-D\n"

def asm_end_program():
        return "(END)\n@END\n0;JMP"

def translate_memory_segment(segment):
    translations = {
        "argument": "ARG",
        "local": "LCL",
        "static": "STATIC",
        "constant": "CONSTANT",
        "this": "THIS",
        "that": "THAT",
        "pointer": "POINTER",
        "temp": "5"
    }
    
    return translations.get(segment, "UNKNOWN")

def main():

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <input_file_path>")
        sys.exit(1)

    input_filename = sys.argv[1]


    parser = Parser(input_filename)
    code_writer = CodeWriter(get_output_filename(input_filename))

    while parser.has_more_commands():
        parsed_line = parser.parse_next()
        code_writer.write_next(parsed_line)

    code_writer.write_terminal()

if __name__ == "__main__":
    main()

