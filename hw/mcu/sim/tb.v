// Icarus testbench for yap_mcu. STATUS read after reset.
// Drive we/re on negedge so posedge samples a stable command.
module tb;
    reg         clk;
    reg         rst;
    reg         we;
    reg         re;
    reg  [7:0]  addr;
    reg  [31:0] wdata;
    wire [31:0] rdata;
    wire [7:0]  ser_tx;
    wire        ser_tx_stb;

    yap_mcu dut (
        .clk(clk),
        .rst(rst),
        .we(we),
        .re(re),
        .addr(addr),
        .wdata(wdata),
        .rdata(rdata),
        .key_we(1'b0),
        .key_in(8'h0),
        .ser_rx_we(1'b0),
        .ser_rx_in(8'h0),
        .ser_tx(ser_tx),
        .ser_tx_stb(ser_tx_stb)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        rst = 1'b1;
        we = 1'b0;
        re = 1'b0;
        addr = 8'h00;
        wdata = 32'h0;
        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        @(posedge clk);
        @(negedge clk);
        addr = 8'h00;
        re = 1'b1;
        we = 1'b0;
        #1;
        $display("STATUS=%08x", rdata);
        @(posedge clk);
        @(negedge clk);
        re = 1'b0;
        $finish;
    end
endmodule
