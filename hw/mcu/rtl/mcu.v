// yap_mcu: poll MMIO bridge. Verilog-2001.
// VDD=3.3 — MCU I/O (no 5-volt part).
// Map: STATUS 0x00, KEY_DATA 0x04, SER_DATA 0x08,
// STOR_LBA 0x0C, STOR_IDX 0x10, STOR_DATA 0x14, STOR_CMD 0x18
module yap_mcu (
    input         clk,
    input         rst,
    input         we,
    input         re,
    input  [7:0]  addr,
    input  [31:0] wdata,
    output [31:0] rdata,
    input         key_we,
    input  [7:0]  key_in,
    input         ser_rx_we,
    input  [7:0]  ser_rx_in,
    output [7:0]  ser_tx,
    output        ser_tx_stb
);
    localparam STATUS    = 8'h00;
    localparam KEY_DATA  = 8'h04;
    localparam SER_DATA  = 8'h08;
    localparam STOR_LBA  = 8'h0C;
    localparam STOR_IDX  = 8'h10;
    localparam STOR_DATA = 8'h14;
    localparam STOR_CMD  = 8'h18;

    wire [7:0] off = {addr[7:2], 2'b00};

    reg [31:0] status;
    reg [31:0] key_data;
    reg [31:0] ser_data;
    reg [31:0] stor_lba;
    reg [31:0] stor_idx;
    reg [31:0] stor_data;
    reg [31:0] stor_cmd;

    assign ser_tx     = 8'h0;
    assign ser_tx_stb = 1'b0;

    assign rdata =
        (off == STATUS)    ? status    :
        (off == KEY_DATA)  ? key_data  :
        (off == SER_DATA)  ? ser_data  :
        (off == STOR_LBA)  ? stor_lba  :
        (off == STOR_IDX)  ? stor_idx  :
        (off == STOR_DATA) ? stor_data :
        (off == STOR_CMD)  ? 32'h0     :
        32'h0;

    always @(posedge clk) begin
        if (rst) begin
            status    <= 32'h0;
            key_data  <= 32'h0;
            ser_data  <= 32'h0;
            stor_lba  <= 32'h0;
            stor_idx  <= 32'h0;
            stor_data <= 32'h0;
            stor_cmd  <= 32'h0;
        end
    end
endmodule
