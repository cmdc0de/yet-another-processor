# Project Goals

design a 32-bit computer


# System board

Files associated with the system board should go into logic folders under the ./system-baoard


* CPU - at mininium ALU is designed with only mosfets
 * I'd like to use a 5V power supply but the mosfets making up the CPU should be 3.3 logic level.
* registers would also like to be make from mosfets as well
* Memory will be SRAM
* Memory bus can be a tristate buffer IC
* GPU  would like to be an FPGA using shared memory with the CPU
* IO can be handled by a small microcontroller feeding data and signals to the CPU
* microcode can be a parallel interface memory IC
* display could be HDMI or SPI but handled by the FPA "GPU"
*

# Operating system

A design from scratch opperating system to make the new CPU and system usable

## Operating system features


## Compiler

* initially just a python application that translates assemblier of this CPU to binary code the CPU understands
* later build a backend for LLVM or gcc

## system emulator

* initially stand alone written in rust 
* later align with qemu



