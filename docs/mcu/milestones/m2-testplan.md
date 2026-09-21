# mcu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| MCU-007 | Inject `key_in=0x41`; STATUS bit 0 is 1; KEY_DATA read is `0x00000041`; STATUS bit 0 is then 0 |
| MCU-008 | Write SER_DATA `0x42`; sim host shows `ser_tx=0x42` with `ser_tx_stb` that cycle |
| MCU-009 | Inject `ser_rx_in=0x43`; STATUS bit 1 is 1; SER_DATA read is `0x00000043`; STATUS bit 1 is then 0 |
| MCU-010 | Buffer words 0=`0xA5A5A5A5` and 1=`0x12345678`, STOR_CMD=1 LBA=0; clobber buffer; STOR_CMD=2; those two words read back |
