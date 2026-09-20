// Icarus testbench: DQ tristate, LE lanes, CE#/OE#/WE#.
module tb_m2;
    reg         clk;
    reg         rst;
    reg  [31:0] addr;
    reg  [31:0] wdata;
    wire [31:0] rdata;
    reg  [2:0]  size;
    reg         re;
    reg         we;
    wire [31:0] DQ;
    wire        ce_n;
    wire        oe_n;
    wire        we_n;
    wire [3:0]  be;

    yap_bus dut (
        .clk(clk),
        .rst(rst),
        .addr(addr),
        .wdata(wdata),
        .rdata(rdata),
        .size(size),
        .re(re),
        .we(we),
        .DQ(DQ),
        .ce_n(ce_n),
        .oe_n(oe_n),
        .we_n(we_n),
        .be(be)
    );

    integer     b;
    reg         dq_z;

    always @(*) begin
        dq_z = 1'b1;
        for (b = 0; b < 32; b = b + 1)
            if (DQ[b] !== 1'bz)
                dq_z = 1'b0;
    end

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        rst = 1'b1;
        addr = 32'h0;
        wdata = 32'h0;
        size = 3'd4;
        re = 1'b0;
        we = 1'b0;
        repeat (3) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        @(posedge clk);
        @(negedge clk);

        $display("IDLE dq_z=%b ce_n=%b oe_n=%b we_n=%b", dq_z, ce_n, oe_n, we_n);

        // store word
        addr = 32'h0;
        wdata = 32'hA5A5A5A5;
        size = 3'd4;
        we = 1'b1;
        re = 1'b0;
        #1;
        $display("STORE_CMD dq_z=%b dq=%08x ce_n=%b oe_n=%b we_n=%b", dq_z, DQ, ce_n, oe_n, we_n);
        @(posedge clk);
        @(negedge clk);
        we = 1'b0;
        @(posedge clk);
        #1;
        $display("AFTER_WORD mem0=%08x", dut.mem[0]);

        // load word: command then data
        re = 1'b1;
        #1;
        $display("LOAD_CMD ce_n=%b oe_n=%b we_n=%b", ce_n, oe_n, we_n);
        @(posedge clk);
        #1;
        $display("LOAD_DATA dq_z=%b dq=%08x", dq_z, DQ);
        @(negedge clk);
        re = 1'b0;
        @(posedge clk);

        @(negedge clk);
        $display("IDLE2 dq_z=%b ce_n=%b oe_n=%b we_n=%b", dq_z, ce_n, oe_n, we_n);

        // byte store at addr 0
        addr = 32'h0;
        wdata = 32'h0000005A;
        size = 3'd1;
        we = 1'b1;
        @(posedge clk);
        @(negedge clk);
        we = 1'b0;
        @(posedge clk);
        #1;
        $display("AFTER_BYTE mem0=%08x", dut.mem[0]);

        // half store at addr 2
        addr = 32'h2;
        wdata = 32'h0000BEEF;
        size = 3'd2;
        we = 1'b1;
        @(posedge clk);
        @(negedge clk);
        we = 1'b0;
        @(posedge clk);
        #1;
        $display("AFTER_HALF mem0=%08x", dut.mem[0]);
        $finish;
    end
endmodule
