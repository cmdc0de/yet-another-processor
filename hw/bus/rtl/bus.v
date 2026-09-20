// yap_bus: CPU memory port to behavioral SRAM. Verilog-2001.
// VDD=3.3 — SRAM and bus (no 5-volt part). LAT_MEM=1: command this
// cycle, data next.
module yap_bus (
    input         clk,
    input         rst,
    input  [31:0] addr,
    input  [31:0] wdata,
    output reg [31:0] rdata,
    input  [2:0]  size,
    input         re,
    input         we,
    inout  [31:0] DQ,
    output        ce_n,
    output        oe_n,
    output        we_n,
    output reg [3:0] be
);
    reg [31:0] mem [0:1023];
    reg        we_r;
    reg        re_r;
    reg [31:0] addr_r;
    reg [31:0] wdata_r;
    reg [2:0]  size_r;
    reg [3:0]  be_r;
    reg [31:0] cpu_dq;
    integer    i;
    integer    idx;
    reg [31:0] tmp;
    reg [31:0] aligned;

    assign ce_n = ~(re | we);
    assign we_n = ~we;
    assign oe_n = ~(re & ~we);

    assign DQ = we ? cpu_dq : 32'bz;
    assign DQ = re_r ? mem[addr_r[11:2]] : 32'bz;

    always @(*) begin
        be = 4'b0000;
        cpu_dq = 32'h0;
        if (size == 3'd4) begin
            be = 4'b1111;
            cpu_dq = wdata;
        end else if (size == 3'd2) begin
            if (addr[1]) begin
                be = 4'b1100;
                cpu_dq = {wdata[15:0], 16'h0};
            end else begin
                be = 4'b0011;
                cpu_dq = {16'h0, wdata[15:0]};
            end
        end else if (size == 3'd1) begin
            if (addr[1:0] == 2'b00) begin
                be = 4'b0001;
                cpu_dq = {24'h0, wdata[7:0]};
            end else if (addr[1:0] == 2'b01) begin
                be = 4'b0010;
                cpu_dq = {16'h0, wdata[7:0], 8'h0};
            end else if (addr[1:0] == 2'b10) begin
                be = 4'b0100;
                cpu_dq = {8'h0, wdata[7:0], 16'h0};
            end else begin
                be = 4'b1000;
                cpu_dq = {wdata[7:0], 24'h0};
            end
        end
    end

    initial begin
        we_r = 1'b0;
        re_r = 1'b0;
        addr_r = 32'h0;
        wdata_r = 32'h0;
        size_r = 3'd4;
        be_r = 4'b0000;
        rdata = 32'h0;
        for (i = 0; i < 1024; i = i + 1)
            mem[i] = 32'h0;
    end

    always @(posedge clk) begin
        if (rst) begin
            we_r    <= 1'b0;
            re_r    <= 1'b0;
            addr_r  <= 32'h0;
            wdata_r <= 32'h0;
            size_r  <= 3'd4;
            be_r    <= 4'b0000;
            rdata   <= 32'h0;
        end else begin
            if (we_r) begin
                idx = addr_r[11:2];
                tmp = mem[idx];
                aligned = wdata_r;
                if (size_r == 3'd2) begin
                    if (addr_r[1])
                        aligned = {wdata_r[15:0], 16'h0};
                    else
                        aligned = {16'h0, wdata_r[15:0]};
                end else if (size_r == 3'd1) begin
                    if (addr_r[1:0] == 2'b00)
                        aligned = {24'h0, wdata_r[7:0]};
                    else if (addr_r[1:0] == 2'b01)
                        aligned = {16'h0, wdata_r[7:0], 8'h0};
                    else if (addr_r[1:0] == 2'b10)
                        aligned = {8'h0, wdata_r[7:0], 16'h0};
                    else
                        aligned = {wdata_r[7:0], 24'h0};
                end
                if (be_r[0]) tmp[7:0]   = aligned[7:0];
                if (be_r[1]) tmp[15:8]  = aligned[15:8];
                if (be_r[2]) tmp[23:16] = aligned[23:16];
                if (be_r[3]) tmp[31:24] = aligned[31:24];
                mem[idx] <= tmp;
            end
            if (re_r) begin
                tmp = mem[addr_r[11:2]];
                if (size_r == 3'd4)
                    rdata <= tmp;
                else if (size_r == 3'd2)
                    rdata <= addr_r[1] ? {16'h0, tmp[31:16]} : {16'h0, tmp[15:0]};
                else if (addr_r[1:0] == 2'b00)
                    rdata <= {24'h0, tmp[7:0]};
                else if (addr_r[1:0] == 2'b01)
                    rdata <= {24'h0, tmp[15:8]};
                else if (addr_r[1:0] == 2'b10)
                    rdata <= {24'h0, tmp[23:16]};
                else
                    rdata <= {24'h0, tmp[31:24]};
            end
            we_r    <= we;
            re_r    <= re;
            addr_r  <= addr;
            wdata_r <= wdata;
            size_r  <= size;
            be_r    <= be;
        end
    end
endmodule
