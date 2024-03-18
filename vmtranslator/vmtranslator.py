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
                self.contents = file.read()
                self.next_line_index = 0
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("An error occurred:", e)

    def parse_next():
        pass

    def has_more_commands(abc):
    # are there more commands to parse?
        return True
        
    def command_type():
    # returns a constant representing the type of the current command
    # C_ARITHMETIC is returned for all the arithmetic/logical commands
        return CommandType.C_ARITHMETIC
    
    def arg1():
    # returns first argument of current command
    # in the case of C_ARITHMETIC, the command itself (add, sub, etc)
    # is returned. Should not be called if the current command
    # is C_RETURN
        return "add"
    
    def arg2():
    # returns the second argument of the current command
    # should be called only if the current command is 
    # C_PUSH, C_POP, C_FUNCTION, or C_CALL
        return 1
    


class CodeWriter:
    def __init__(output_file):
    # opens the output file/stream and gets it ready to write to
        pass

    def write_next():
        pass
    
    def write_arithmetic(command):
    # writes to the output file the assembly code that implements
    #  the given arithmetic command
        pass
    
    def write_push_pop(command, segment, index):
    # `command` is C_PUSH or C_POP, segment is a string, index is an int
    # writes to the output file the assembly code that implements the given command
    #  where command is either C_POP or C_PUSH
        pass
    
    def close():
    # closes the output file
        pass

def get_output_filename(input_filename):
    
    file_name, _ = os.path.splitext(os.path.basename(input_filename))
    output_filename = f"{file_name}.asm"
    
    return output_filename

def main():

    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py <input_file_path>")
        sys.exit(1)

    input_filename = sys.argv[1]

    parser = Parser()
    code_writer = CodeWriter(get_output_filename(input_filename))

    while parser.has_more_commands():
        parsed_line = parser.parse_next()
        code_writer.write_next(parsed_line)

if __name__ == "__main__":
    main()

