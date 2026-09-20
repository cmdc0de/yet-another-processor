# FPGA GPU features

Prefix: `GPU`

Separate FPGA from the CPU-emulator FPGA. First GPU is a display engine: backbuffer the OS can blit. Physical output (SPI or HDMI) is a design-time choice. Not a 3D shader GPU. Not MCU I/O. Not Memory + bus.

Implementation: `gpu/`. Tests under `compiler/tests/`. v1 is **simulation** on Linux. Synthesis to a board is later-generation. Pixel format, resolution, SPI vs HDMI, and the CPU port map are `design.md` after this catalog.

## Tree and sim

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| GPU-001 | ~~HDL sources under `gpu/`~~ | done | m1 |
| GPU-002 | ~~Simulation builds and runs on Linux (dev host)~~ | done | m1 |
| GPU-003 | ~~Tests fail if the chosen simulator is missing~~ | done | m1 |

## Backbuffer

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| GPU-004 | ~~One backbuffer in GPU memory (not CPU SRAM scanout)~~ | done | m1 |
| GPU-005 | ~~Documented pixel format and at least one named resolution (`design.md`)~~ | done | m1 |
| GPU-006 | ~~Test dump of the backbuffer (raw or PPM) matches a known fill~~ | done | m1 |

## Host blit

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| GPU-007 | CPU-visible port so software can write the backbuffer | open | |
| GPU-008 | Fill or blit a rectangle of pixels into the backbuffer | open | |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| GPU-009 | Synthesize to a named FPGA part | open | later-generation |
| GPU-010 | Real SPI or HDMI PHY on a board | open | later-generation |
| GPU-011 | 3D / shader pipeline | open | later-generation |
