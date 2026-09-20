// yap_bus: CPU memory port to behavioral SRAM. Verilog-2001.
// VDD=3.3 — SRAM and bus (no 5-volt part). LAT_MEM=1: command this
// cycle, data next. Byte lanes / CE# OE# WE# are later (MEMORY-BUS-003-005).
module yap_bus (
    input         clk,
    input         rst,
    input  [31:0] addr,
    input  [31:0] wdata,
    output reg [31:0] rdata,
    input  [2:0]  size,
    input         re,
    input         we
);
    reg [31:0] mem [0:1023];
    reg        we_r;
    reg        re_r;
    reg [31:0] addr_r;
    reg [31:0] wdata_r;
    integer    i;

    initial begin
        we_r = 1'b0;
        re_r = 1'b0;
        addr_r = 32'h0;
        wdata_r = 32'h0;
        rdata = 32'h0;
        for (i = 0; i < 1024; i = i + 1)
            mem[i] = 32'h0;
    end

    always @(posedge clk) begin
        if (rst) begin
            we_r   <= 1'b0;
            re_r   <= 1'b0;
            addr_r <= 32'h0;
            wdata_r <= 32'h0;
            rdata  <= 32'h0;
        end else begin
            if (we_r)
                mem[addr_r[11:2]] <= wdata_r;
            if (re_r)
                rdata <= mem[addr_r[11:2]];
            we_r    <= we;
            re_r    <= re;
            addr_r  <= addr;
            wdata_r <= wdata;
        end
    end
endmodule
