// Dump f0-f31 after reset (IEEE-754 binary32 zeros).
module tb;
    reg     clk;
    reg     rst;
    integer i;

    yap_fpu dut (
        .clk(clk),
        .rst(rst)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        rst = 1'b1;
        repeat (4) @(posedge clk);
        rst = 1'b0;
        @(posedge clk);
        #1;
        for (i = 0; i < 32; i = i + 1)
            $display("F%0d=%08x", i, dut.f[i]);
        $finish;
    end
endmodule
