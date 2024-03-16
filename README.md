# pyvmtranslator

This repo contains my implementation of the first project from Nand2Tetris (part 2), which converts VM code into Hack assembly code.

## Implementation notes (remove when completed)

3 classes:
* Parser (to parse each VM command into lexical elements)
* CodeWriter (to write the assembly code that implements the parsed command)
* Main (drives the process)

Main (VMTranslator)
* input = filename.vm and output = filename.asm
* constructs parser, constructs codewriter, and then goes through each row generating the relevant code

Parser:
* Handles parsing of `.vm` file
* Reads a VM command, parses command into lexical components and provides convenient access to them
* Ignores all whitespace and comments
* Routines:
   * Constructor - takes as arg the input file and opens it ready to parse it
   * hasMoreCommands - boolean; is there more stuff to parse?
   * advance - reads next command from input and makes it the current one; only called if hasMoreCommands is true
   * commandType etc - see below:
  ![image](https://github.com/thisisnic/pyvmtranslator/assets/13715823/83d3143a-674d-424e-a5b8-26a43f15ba75)

CodeWriter

![image](https://github.com/thisisnic/pyvmtranslator/assets/13715823/db70b0dc-5916-4f0e-b41a-cc5afbc46d3c)

  


### Test Steps:###

1. Run the VM programme in the VM emulator to understand what it is doing
2. Use your translator to generate the assembly code
   • it can be helpful to output comments containing the VM code so it's easier to debug later
3. Load ...`.tst` file into the CPU emulator and inspect results (cant use `.asm` file as there are some initialization steps we need but haven't done in this project)

## Example usage

To run the code:

```py
python3 ./vmtranslator/vmtranslator.py ./MemoryAccess/BasicTest/BasicTest.vm
```



