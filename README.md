# pyvmtranslator

This repo contains my implementation of the first project from Nand2Tetris (part 2), which converts VM code into Hack assembly code.

## Example usage

To run the code:

```py
python3 ./vmtranslator/vmtranslator.py ./MemoryAccess/BasicTest/BasicTest.vm
```

## Implementation notes (remove when completed)

### Big Picture

![image](https://github.com/thisisnic/pyvmtranslator/assets/13715823/e8b10896-403d-4884-82d0-40a41b269664)



### Test Steps:

1. Run the VM programme in the VM emulator to understand what it is doing
2. Use your translator to generate the assembly code
   • it can be helpful to output comments containing the VM code so it's easier to debug later
3. Load ...`.tst` file into the CPU emulator and inspect results (cant use `.asm` file as there are some initialization steps we need but haven't done in this project)




