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
        pass

    def write_next(self, line):
        try:
            with open(self.filename, 'a') as file:
                file.write(f"//{line['og_line']}\n")
                # do some parsing stuff here
                # write the parsed version of the line to the file

        except Exception as e:
                print("An error occurred while writing to the file:", e)
    
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

    parser = Parser(input_filename)
    code_writer = CodeWriter(get_output_filename(input_filename))

    while parser.has_more_commands():
        parsed_line = parser.parse_next()
        code_writer.write_next(parsed_line)

if __name__ == "__main__":
    main()

