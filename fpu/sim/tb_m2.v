// COP1 add.s/sub.s/mul.s/div.s on yap_fpu. IEEE-754 binary32.
// Drive we on negedge so posedge samples a stable command.
module tb_m2;
    reg        clk;
    reg        rst;
    reg        we;
    reg [4:0]  fd;
    reg [4:0]  fs;
    reg [4:0]  ft;
    reg [5:0]  funct;

    yap_fpu dut (
        .clk(clk),
        .rst(rst),
        .we(we),
        .fd(fd),
        .fs(fs),
        .ft(ft),
        .funct(funct)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task loadf;
        input [4:0]  idx;
        input [31:0] val;
        begin
            @(negedge clk);
            dut.f[idx] = val;
        end
    endtask

    task exec_op;
        input [4:0] d;
        input [4:0] s;
        input [4:0] t;
        input [5:0] fn;
        begin
            @(negedge clk);
            fd = d;
            fs = s;
            ft = t;
            funct = fn;
            we = 1'b1;
            @(posedge clk);
            @(negedge clk);
            we = 1'b0;
        end
    endtask

    initial begin
        rst = 1'b1;
        we = 1'b0;
        fd = 5'd0;
        fs = 5'd0;
        ft = 5'd0;
        funct = 6'd0;
        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        @(posedge clk);

        loadf(5'd2, 32'h3F800000);
        loadf(5'd3, 32'h40000000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd0);
        #1;
        $display("ADD=%08x", dut.f[1]);

        loadf(5'd2, 32'h3F800000);
        loadf(5'd3, 32'h3F000000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd1);
        #1;
        $display("SUB=%08x", dut.f[1]);

        loadf(5'd2, 32'h40000000);
        loadf(5'd3, 32'h40400000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd2);
        #1;
        $display("MUL=%08x", dut.f[1]);

        loadf(5'd2, 32'h3F800000);
        loadf(5'd3, 32'h40000000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd3);
        #1;
        $display("DIV=%08x", dut.f[1]);

        loadf(5'd2, 32'h3F800000);
        loadf(5'd3, 32'h00000000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd3);
        #1;
        $display("DIV0=%08x", dut.f[1]);

        loadf(5'd2, 32'h00000000);
        loadf(5'd3, 32'h00000000);
        exec_op(5'd1, 5'd2, 5'd3, 6'd3);
        #1;
        $display("DIV00=%08x", dut.f[1]);

        $finish;
    end
endmodule
