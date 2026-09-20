// MMIO fill then dump YAP-160 as PPM P6.
module tb_m2;
    reg         clk;
    reg         rst;
    reg         we;
    reg  [7:0]  addr;
    reg  [31:0] wdata;
    integer     fd;
    integer     x;
    integer     y;
    integer     idx;
    integer     code;
    reg [8*256-1:0] ppm_path;
    reg [31:0]  pix;

    yap_gpu dut (
        .clk(clk),
        .rst(rst),
        .we(we),
        .addr(addr),
        .wdata(wdata)
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
            @(posedge clk);
            @(negedge clk);
            we = 1'b0;
        end
    endtask

    initial begin
        rst = 1'b1;
        we = 1'b0;
        addr = 8'h00;
        wdata = 32'h0;
        repeat (4) @(posedge clk);
        @(negedge clk);
        rst = 1'b0;
        @(posedge clk);

        poke(8'h04, 32'h00FF0000);
        poke(8'h08, 32'd0);
        poke(8'h0c, 32'd0);
        poke(8'h10, 32'd8);
        poke(8'h14, 32'd8);
        poke(8'h00, 32'd1);
        @(posedge clk);
        #1;

        code = $value$plusargs("PPM=%s", ppm_path);
        if (code == 0)
            ppm_path = "fb.ppm";
        fd = $fopen(ppm_path, "wb");
        $fwrite(fd, "P6\n160 120\n255\n");
        for (y = 0; y < 120; y = y + 1) begin
            for (x = 0; x < 160; x = x + 1) begin
                idx = y * 160 + x;
                pix = dut.fb[idx];
                $fwrite(fd, "%c%c%c", pix[23:16], pix[15:8], pix[7:0]);
            end
        end
        $fclose(fd);
        $finish;
    end
endmodule
