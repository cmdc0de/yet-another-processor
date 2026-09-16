# Project Goals

## Project description

Design and implement a full computer system: CPU, GPU, operating system, compiler, and two emulators — one to test the operating system, one to test the CPU.

The machine is 32-bit. The board is powered at 5 V. A regulator drops the CPU core to 3.3 V.

The CPU is a discrete MOSFET design with a RISC-shaped, load/store programmer model and microcoded control. The ALU, flags register, and 16 of 32 general-purpose registers are CMOS MOSFETs. The other 16 GPRs are ICs. Software sees one 32-register file. If the MOSFET register file is too large to build, more (or all) of those 32 registers move to ICs without changing the ISA.

ICs are also allowed for microcode storage, instruction cache, data cache, and tristate buffers. Main memory is SRAM.

The GPU is an FPGA, separate from the CPU-emulator FPGA. The first GPU is a display engine: SPI or HDMI output with a backbuffer. Physical output is chosen at GPU design time. This is not a 3D shader GPU.

The compiler starts as a Python program that translates this CPU’s assembly to machine code. It may later become a Rust compiler. LLVM and GCC backends are not the plan.

The emulator used to write and test the operating system is written in Rust. The emulator used to test the CPU design is a different FPGA.

I/O other than the GPU is a microcontroller bridge (STM32 is the current candidate; the exact part is not a goals decision).

A floating-point unit is in scope as a coprocessor (IC or FPGA), not MOSFETs. Virtual memory is a later generation: the first CPU and OS use privilege plus simple memory protection, and the ISA reserves encodings and exceptions for translation later.

## Constraints

| Topic | Decision |
|---|---|
| Word size | 32-bit |
| Power | 5 V system rail, 3.3 V CPU via regulator. Prefer 3.3 V for the bus; level-shift only if a part forces 5 V |
| ISA | Custom, RISC-shaped (load/store), microcoded. Encodings are a later design document |
| GPRs | 32 architectural. First CPU: 16 MOSFET + 16 IC, one file to software |
| GPR fallback | More of the 32 may move to ICs; ISA still has 32 |
| MOSFET (intent) | ALU, flags, 16 GPRs |
| IC allowed | Other 16 GPRs, microcode, I-cache, D-cache, tristate buffers |
| Main memory | SRAM |
| Memory model | User/supervisor + base/limit or MPU on the first CPU. Virtual memory reserved in the ISA. No MMU on v1 hardware |
| FPU | Coprocessor, IC or FPGA, not MOSFET. Software float until it exists |
| Integer mul/div | Not specified here; ALU design document |
| GPU | Separate FPGA, backbuffer, SPI or HDMI |
| Compiler | Python first, Rust compiler later. Not LLVM/GCC |
| OS test harness | Rust emulator |
| CPU test harness | Separate FPGA |
| I/O | MCU bridge (STM32 candidate) |

`r0` wired-to-zero vs a real register, MPU vs a single base/limit, IEEE-754 vs a simpler float format, and cache internals are not goals decisions.

## Non-goals (this generation)

- 3D / shader GPU
- MOSFET FPU, MOSFET caches, MOSFET microcode, MOSFET tristate
- MMU / page tables on the first CPU
- QEMU target
- LLVM or GCC backend
- Custom silicon

## Honesty

- Sixteen 32-bit MOSFET registers plus a 32-bit MOSFET ALU is a large SOT-23 board. That is accepted. Further fallback is moving GPRs to ICs, not shrinking the ISA.
- A split register file means two physical timings and extra muxing. The FPGA CPU should model that split if it is meant to test the physical CPU. The Rust OS emulator only needs 32 register names.
- Discrete MOSFET logic will be slow (Hz–kHz class until measured). That is not a defect.
- The first OS is protected, not paged. Virtual memory is an ISA-compatible later generation, not Linux in year one.
- FPU in scope does not mean MOSFET float and does not mean FP on the first board.
- “Cache IC” means SRAM plus hit/tag logic somewhere (glue, FPGA, or later). That is a CPU-design detail.
- Two FPGAs have two jobs (CPU emulator vs GPU) and stay separate projects. The FPU may share the CPU-emulator FPGA for bring-up or be its own IC/FPGA; it does not live on the GPU FPGA.

## Subprojects

| Subproject | Job | Done means |
|---|---|---|
| ISA + ABI | Contract for CPU, both emulators, compiler, OS | Frozen encodings, 32 GPRs, flags, privilege, reserved VM traps, coprocessor/FPU space, calling convention |
| Python compiler (v1) | Assembly → machine code | Builds OS and tests; output runs on the Rust emulator |
| Rust OS emulator | Write and test the OS before the MOSFET CPU exists | Boots the OS, passes ISA tests |
| Operating system | Make the machine usable | Kernel, syscalls, simple protection on Rust, then FPGA CPU, then MOSFET CPU |
| MOSFET cell library | Gates, latches, adder bit | Characterized cells (already started in `lt-spice/`) |
| CPU microarchitecture | Datapath + microcode that implements the ISA | Spec the FPGA CPU can be written from, including the split register file |
| FPGA CPU emulator | Test the CPU design | Matches Rust on ISA tests; can run the OS or a subset |
| Physical CPU | MOSFET ALU, flags, 16 GPRs + IC GPRs, control, caches, bus | Same binaries as the emulators |
| FPU coprocessor | FP ops off the MOSFET datapath | IC or FPGA the ISA can target; OS save/restore |
| Memory + bus | SRAM + tristate | Documented protocol at CPU clock |
| FPGA GPU | Display | Backbuffered SPI or HDMI; OS can blit a framebuffer |
| MCU I/O | Keyboard, serial, storage | Protocol the OS talks to |
| Rust compiler (later) | Higher-level language | After the Python compiler is no longer enough |

## Sequencing principles

Project success is the full machine. Work order is contract-first: the MOSFET CPU is not the first place the ISA is tested. Slice the build, not the architecture (32-bit, 32 GPRs, reserved VM, coprocessor FPU in the ISA from day one).

1. This goals document.
2. ISA + ABI design document.
3. Python assembler and ISA tests.
4. Rust OS emulator; OS work starts here (privilege + simple protection, no paging).
5. MOSFET cell library continues in parallel (already started; does not wait on the ISA).
6. CPU microarchitecture and microcode; FPGA CPU checked against Rust and the ISA tests.
7. Physical CPU in slices: 1-bit latch → flags bit → ALU bit → 32-bit ALU → 16 MOSFET GPRs + 16 IC GPRs → microcode, caches, tristate.
8. System: SRAM, bus, GPU FPGA, MCU, 5 V / 3.3 V power.
9. Same OS binaries on Rust → FPGA CPU → MOSFET CPU.
10. FPU coprocessor after integer programs work; software float until then.
11. Reserved virtual memory only after the protected-mode kernel is real.
12. Rust compiler when the assembler is no longer enough.

Milestone plans (`docs/project_plan/`) come after the ISA design, not before.

## Repository layout

Implementation does not live under `docs/`.

```
docs/            goals, ISA, CPU, OS, GPU, plans
lt-spice/        MOSFET cell simulations (exists)
hw/              KiCad, CPU PCBs, system board
emu/rust/        OS / ISA emulator
emu/fpga-cpu/    CPU-design FPGA
gpu/             GPU FPGA
compiler/        Python v1, Rust later
os/
```

Datasheets and footprints stay under `docs/` (the existing `docs/componets/` spelling should be fixed when that directory is touched). Existing `lt-spice/` work is the start of the MOSFET cell library.
