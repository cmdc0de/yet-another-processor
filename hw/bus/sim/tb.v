// Icarus testbench for yap_bus. LAT_MEM=1 word roundtrip.
// Drive controls on negedge so posedge samples a stable command.
module tb;
    reg         clk;
    reg         rst;
    reg  [31:0] addr;
    reg  [31:0] wdata;
    wire [31:0] rdata;
    reg  [2:0]  size;
    reg         re;
    reg         we;

    yap_bus dut (
        .clk(clk),
        .rst(rst),
        .addr(addr),
        .wdata(wdata),
        .rdata(rdata),
        .size(size),
        .re(re),
        .we(we)
    );

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

        // command cycle: store
        addr = 32'h0;
        wdata = 32'hA5A5A5A5;
        size = 3'd4;
        we = 1'b1;
        re = 1'b0;
        @(posedge clk);
        #1;
        $display("AFTER_WE mem0=%08x rdata=%08x we_r=%b", dut.mem[0], rdata, dut.we_r);

        // next cycle: write commits; start load
        @(negedge clk);
        we = 1'b0;
        re = 1'b1;
        @(posedge clk);
        #1;
        $display("AFTER_COMMIT mem0=%08x rdata=%08x", dut.mem[0], rdata);

        // next cycle: rdata valid
        @(negedge clk);
        re = 1'b0;
        @(posedge clk);
        #1;
        $display("AFTER_RE rdata=%08x", rdata);
        $finish;
    end
endmodule
