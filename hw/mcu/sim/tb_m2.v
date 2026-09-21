// Icarus testbench for yap_mcu m2: key, serial, storage.
// Drive we/re/injects on negedge so posedge samples a stable command.
module tb_m2;
    reg         clk;
    reg         rst;
    reg         we;
    reg         re;
    reg  [7:0]  addr;
    reg  [31:0] wdata;
    wire [31:0] rdata;
    reg         key_we;
    reg  [7:0]  key_in;
    reg         ser_rx_we;
    reg  [7:0]  ser_rx_in;
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
        .key_we(key_we),
        .key_in(key_in),
        .ser_rx_we(ser_rx_we),
        .ser_rx_in(ser_rx_in),
        .ser_tx(ser_tx),
        .ser_tx_stb(ser_tx_stb)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task poke;
        input [7:0]  a;
        input [31:0] d;
        begin
            @(negedge clk);
            addr = a;
            wdata = d;
            we = 1'b1;
            re = 1'b0;
            key_we = 1'b0;
            ser_rx_we = 1'b0;
            @(posedge clk);
            @(negedge clk);
            we = 1'b0;
        end
    endtask

    task peek;
        input  [7:0]  a;
        output [31:0] d;
        begin
            @(negedge clk);
            addr = a;
            we = 1'b0;
            re = 1'b1;
            key_we = 1'b0;
            ser_rx_we = 1'b0;
            #1;
            d = rdata;
            @(posedge clk);
            @(negedge clk);
            re = 1'b0;
        end
    endtask

    task inject_key;
        input [7:0] k;
        begin
            @(negedge clk);
            key_in = k;
            key_we = 1'b1;
            we = 1'b0;
            re = 1'b0;
            ser_rx_we = 1'b0;
            @(posedge clk);
            @(negedge clk);
            key_we = 1'b0;
        end
    endtask

    task inject_ser;
        input [7:0] b;
        begin
            @(negedge clk);
            ser_rx_in = b;
            ser_rx_we = 1'b1;
            we = 1'b0;
            re = 1'b0;
            key_we = 1'b0;
            @(posedge clk);
            @(negedge clk);
            ser_rx_we = 1'b0;
        end
    endtask

    reg [31:0] got;

    initial begin
        rst = 1'b1;
        we = 1'b0;
        re = 1'b0;
        addr = 8'h00;
        wdata = 32'h0;
        key_we = 1'b0;
        key_in = 8'h0;
        ser_rx_we = 1'b0;
        ser_rx_in = 8'h0;
        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        @(posedge clk);

        inject_key(8'h41);
        peek(8'h00, got);
        $display("KEY_STATUS=%08x", got);
        peek(8'h04, got);
        $display("KEY_DATA=%08x", got);
        peek(8'h00, got);
        $display("KEY_STATUS2=%08x", got);

        @(negedge clk);
        addr = 8'h08;
        wdata = 32'h42;
        we = 1'b1;
        re = 1'b0;
        @(posedge clk);
        #1;
        $display("SER_TX=%02x STB=%b", ser_tx, ser_tx_stb);
        @(negedge clk);
        we = 1'b0;

        inject_ser(8'h43);
        peek(8'h00, got);
        $display("SER_STATUS=%08x", got);
        peek(8'h08, got);
        $display("SER_DATA=%08x", got);
        peek(8'h00, got);
        $display("SER_STATUS2=%08x", got);

        poke(8'h0C, 32'h0);
        poke(8'h10, 32'h0);
        poke(8'h14, 32'hA5A5A5A5);
        poke(8'h14, 32'h12345678);
        poke(8'h18, 32'd1);
        poke(8'h10, 32'h0);
        poke(8'h14, 32'hFFFFFFFF);
        poke(8'h14, 32'hFFFFFFFF);
        poke(8'h18, 32'd2);
        poke(8'h10, 32'h0);
        peek(8'h14, got);
        $display("STOR_W0=%08x", got);
        peek(8'h14, got);
        $display("STOR_W1=%08x", got);

        $finish;
    end
endmodule
