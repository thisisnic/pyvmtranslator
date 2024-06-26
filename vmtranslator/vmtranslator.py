from enum import Enum
import os
import sys
import re
import tempfile

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
        # get the line
        line_to_parse = self.contents[self.next_line_index]

        # remove any comments and whitespace
        line_to_parse = re.sub(re.compile("//.*"), "", line_to_parse).strip()
        
        self.next_line_index += 1

        if line_to_parse != "":
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
        if line.startswith("return"):
            return CommandType.C_RETURN
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
        self.set_filename(output_file)
        self.logical_label_num = 0
        self.return_num = 0
        if os.path.isfile(output_file):
            os.remove(output_file)

    def set_filename(self, filename):
        self.filename = filename

    def write_next(self, line):
        try:
            with open(self.filename, 'a') as file:
                file.write(f"//{line['og_line']}\n")
        except Exception as e:
                print("An error occurred while writing to the file:", e)

        if line['command_type'] == CommandType.C_ARITHMETIC:
            self.write_arithmetic(line['arg1'])

        elif line['command_type'] in [CommandType.C_PUSH, CommandType.C_POP]:
            self.write_push_pop(line['command_type'], line['arg1'], line['arg2'])

        elif line['command_type'] == CommandType.C_LABEL:
            self.write_label(line['arg1'])
        elif line['command_type'] == CommandType.C_CALL:
            self.write_call(line['arg1'], int(line['arg2'])), 
        elif line['command_type'] == CommandType.C_FUNCTION:
            self.write_function(line['arg1'], int(line['arg2']))
        elif line['command_type'] == CommandType.C_GOTO:
            self.write_goto(line['arg1'])
        elif line['command_type'] == CommandType.C_IF:
            self.write_if(line['arg1'])
        elif line['command_type'] == CommandType.C_RETURN:
            self.write_return(line['arg1'], line['arg2'])


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
                
    def write_init(self):

        init_code = "@256\nD=A\n@0\nM=D\n"

        try:
            with open(self.filename, 'a') as file:
                file.write(init_code)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

        self.write_call("Sys.init", 0)

    def write_label(self, label):

        label_assembly = "(" + label + ")\n"
        try:
            with open(self.filename, 'a') as file:
                file.write(label_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    def write_goto(self, label):

        goto_assembly = f"@{label}\n0;JMP\n"
        try:
            with open(self.filename, 'a') as file:
                file.write(goto_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    def write_if(self, label):

        ifgoto_assembly = f"@SP\nA=M-1\nD=M\n@SP\nM=M-1\n@{label}\nD;JGT\n"
        try:
            with open(self.filename, 'a') as file:
                file.write(ifgoto_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    # TODO: write assembly code for function command
    def write_function(self, function_name, num_vars):
        label = "(" + function_name + ")\n"
        setup_local = ("@SP\nD=M\n@LCL\nM=D\n" + "@SP\nA=M\nM=0\n@SP\nM=M+1\n" * num_vars)
        function_assembly = label + setup_local
        
        try:
            with open(self.filename, 'a') as file:
                file.write(function_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    # TODO: write assembly code for call command
    def write_call(self, function_name, num_args):

        # 1. set the arg pointer to the address of the first of the N values which are arguments to our function
# We now know what is above the arg pointer is the working stack of the caller and what is below the args is the arguments of the callee
# 2. save the state of the caller. stack is safe but need to know the segments, so we save (in order from top to bottom): return address, LCL, ARG, THIS, THAT
# 3. Jump to execute function Foo
        memory_setup = ""
        return_label = f"(RET_ADDRESS_CALL{self.return_num})\n"
        call_assembly = memory_setup + f"@{function_name}\n0;JMP\n" + return_label
        
        try:
            with open(self.filename, 'a') as file:
                file.write(call_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)

    # TODO: write assembly code for return command
    def write_return(self, function_name, num_args):

        # get the return address and save in R14
        return_assembly = "@LCL\nD=M\n@R13\nM=D\n@R13\nD=M\n@5\nD=D-A\nA=D\nD=M\n@14\nM=D\n"

# The return command:
# 1. take the topmost value from the stack and copy it into argument 0
        return_assembly = return_assembly + "@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n"    
# 2. restore the segment pointers of the caller
        return_assembly = return_assembly + "@R13\nD=M\n@LCL\nD=D-A\nA=D\nD=M\n"
        
        count = 2
        for segment in ['THAT', 'THIS', 'ARG']:
            return_assembly = return_assembly + f"@{segment}\nM=D\n@13\nD=M\n@{count}\nD=D-A\nA=D\nD=M\n"
            count += 1 
# 5. Jump to return address within caller's code
        return_assembly = return_assembly + "@LCL\nM=D\n@14\nA=M\n"
    
        try:
            with open(self.filename, 'a') as file:
                file.write(return_assembly)
        except Exception as e:
                print("An error occurred while writing to the file:", e)



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


def get_output_filename(input_filename, is_dir = False):

    if is_dir:
        file_name = os.path.basename(input_filename.rstrip("/"))
    else:
        file_name, _ = os.path.splitext(os.path.basename(input_filename))
    
    output_filename = f"{file_name}.asm"

    out_path = os.path.dirname(input_filename) + "/" + output_filename

    return out_path


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

    input = sys.argv[1]

    isfile = os.path.isfile(input) and os.path.splitext()[1] == ".vm"
    isdir = os.path.isdir(input)

    if not isfile and not isdir:
        print("neither file nor dir")

    outfile = get_output_filename(input, isdir)

    # if input is a directory, scan for all VM files and dump then in a tempfile with sys.vm last
    if isdir:
        vm_files = [f for f in os.listdir(input) if f.endswith('.vm')]
        if not vm_files:
            print("No .vm files found.")
        
        if 'Sys.vm' in vm_files:
            vm_files.remove('Sys.vm')
            vm_files.append('Sys.vm')

        file_name = os.path.basename(input) + ".vm"

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".vm", prefix=file_name) as temp_file:
            for vm_file in vm_files:
                with open(os.path.join(input, vm_file), 'r') as file:
                    temp_file.write(file.read())
                    temp_file.write("\n")

        input = temp_file.name
        print(f"Files dumped to {temp_file.name}")

    parser = Parser(input)

    code_writer = CodeWriter(outfile)

    if isdir:
        code_writer.write_init()

    while parser.has_more_commands():
        parsed_line = parser.parse_next()
        if parsed_line:
            code_writer.write_next(parsed_line)

    code_writer.write_terminal()

if __name__ == "__main__":
    main()

