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
    output reg [7:0]  ser_tx,
    output reg        ser_tx_stb
);
    localparam STATUS    = 8'h00;
    localparam KEY_DATA  = 8'h04;
    localparam SER_DATA  = 8'h08;
    localparam STOR_LBA  = 8'h0C;
    localparam STOR_IDX  = 8'h10;
    localparam STOR_DATA = 8'h14;
    localparam STOR_CMD  = 8'h18;

    wire [7:0] off = {addr[7:2], 2'b00};

    reg        key_ready;
    reg [31:0] key_data;
    reg        ser_rx_ready;
    reg [31:0] ser_data;
    reg [31:0] stor_lba;
    reg [31:0] stor_idx;
    reg [31:0] xfer [0:127];
    reg [31:0] stor [0:2047];
    integer    i;
    integer    j;

    wire        idx_ok = (stor_idx <= 32'd127);
    wire [31:0] status = {30'h0, ser_rx_ready, key_ready};
    wire [31:0] stor_rdata = idx_ok ? xfer[stor_idx[6:0]] : 32'h0;

    assign rdata =
        (off == STATUS)    ? status                              :
        (off == KEY_DATA)  ? (key_ready ? key_data : 32'h0)      :
        (off == SER_DATA)  ? (ser_rx_ready ? ser_data : 32'h0)   :
        (off == STOR_LBA)  ? stor_lba                            :
        (off == STOR_IDX)  ? stor_idx                            :
        (off == STOR_DATA) ? stor_rdata                          :
        32'h0;

    always @(posedge clk) begin
        ser_tx_stb <= 1'b0;
        if (rst) begin
            key_ready    <= 1'b0;
            key_data     <= 32'h0;
            ser_rx_ready <= 1'b0;
            ser_data     <= 32'h0;
            stor_lba     <= 32'h0;
            stor_idx     <= 32'h0;
            ser_tx       <= 8'h0;
            ser_tx_stb   <= 1'b0;
            for (i = 0; i < 128; i = i + 1)
                xfer[i] <= 32'h0;
            for (j = 0; j < 2048; j = j + 1)
                stor[j] <= 32'h0;
        end else begin
            if (key_we) begin
                key_data  <= {24'h0, key_in};
                key_ready <= 1'b1;
            end
            if (ser_rx_we) begin
                ser_data     <= {24'h0, ser_rx_in};
                ser_rx_ready <= 1'b1;
            end
            if (we) begin
                if (off == SER_DATA) begin
                    ser_tx     <= wdata[7:0];
                    ser_tx_stb <= 1'b1;
                end else if (off == STOR_LBA) begin
                    stor_lba <= wdata;
                end else if (off == STOR_IDX) begin
                    stor_idx <= wdata;
                end else if (off == STOR_DATA) begin
                    if (idx_ok) begin
                        xfer[stor_idx[6:0]] <= wdata;
                        if (stor_idx == 32'd127)
                            stor_idx <= 32'h0;
                        else
                            stor_idx <= stor_idx + 32'd1;
                    end
                end else if (off == STOR_CMD) begin
                    if (wdata == 32'd1 && stor_lba < 32'd16) begin
                        for (i = 0; i < 128; i = i + 1)
                            stor[(stor_lba * 128) + i] <= xfer[i];
                    end else if (wdata == 32'd2 && stor_lba < 32'd16) begin
                        for (i = 0; i < 128; i = i + 1)
                            xfer[i] <= stor[(stor_lba * 128) + i];
                    end
                end
            end
            if (re) begin
                if (off == KEY_DATA)
                    key_ready <= 1'b0;
                else if (off == SER_DATA)
                    ser_rx_ready <= 1'b0;
                else if (off == STOR_DATA) begin
                    if (idx_ok) begin
                        if (stor_idx == 32'd127)
                            stor_idx <= 32'h0;
                        else
                            stor_idx <= stor_idx + 32'd1;
                    end
                end
            end
        end
    end
endmodule
