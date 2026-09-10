# Project Goals

design a 32-bit computer


# System board

Files associated with the system board should go into logic folders under the ./system-board
The system board should have sub folders for each major component of the computer.

Folder Structure under docs, if ends with .md its a file if no file extension its a folder. Items inside << >> means use the standard project layout

* docs
    * components
      * ... datasheets for components are considering using
    * project-goals.md
    * project_plan
      * milestones
        * m1-plan.md
        * m1-testplan.md
        * ...
        * m{N}-plan.md
        * m{n}-testplan.md
    * computer
      * system_board.md 
      * CPU
        * cpu.md
        * registers.md
        * ALU.md
        * FPU.md
        * control_logic.md
        * microcode.md
        * code_cache.md (L1 cache)
      * memory_bus.md
      * memory.md
      * SRAM.md
      * GPU (implemented via FPGA)
        * gpu_memory.md
        * gpu_design.md
    * Complier
      * compiler_design.md
      * implementation_phases.md
      * milestones
        * m1-plan.md
        * m1-testplan.md
        * ...
        * m{N}-plan.md
        * m{n}-testplan.md
    * Operating System
      * os_design_principals.md
      * ABI.md
      * system_call_interface.md
    * emulator
      * rust
        * docs
          * software_emulator_design.md
        * << standard rust project layout >>
      * FPGA
        * docs
          * design.md
        * << standard FPGA project layout >>


# Project anchors / design goals

* CPU - at minium ALU is designed with only mosfets
  * I'd like to use a 5V power supply but the mosfets making up the CPU should be 3.3 logic level.
* registers would also like to be make from mosfets as well
* RAM Memory will be SRAM
* Memory bus can be a tristate buffer IC
* GPU  would like to be an FPGA 
* IO can be handled by a small microcontroller feeding data and signals to the CPU
* microcode can be a parallel interface memory IC
* display could be HDMI or SPI but handled by the FPA "GPU"
* emulator is to test the ISA of the CPU as well as allow me to start writing the operating system before the CPU is actually built

# Operating system

A design from scratch operating system to make the new CPU and system usable

## Operating system features

* 32 bit real and protected mode

## Compiler

* initially just a python application that translates assemblier of this CPU to binary code the CPU understands
* later build a backend for LLVM or gcc

## system emulator

* initially stand alone written in rust 
  * goal to test operating system
  * later align with qemu
* another written for an FPGA 
  * goal to test CPU




