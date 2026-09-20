// Dump YAP-160 backbuffer as PPM P6 after reset.
module tb;
    reg clk;
    reg rst;
    integer fd;
    integer x;
    integer y;
    integer idx;
    integer code;
    reg [8*256-1:0] ppm_path;
    reg [31:0] pix;

    yap_gpu dut (
        .clk(clk),
        .rst(rst),
        .we(1'b0),
        .addr(8'h00),
        .wdata(32'h0)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        rst = 1'b1;
        repeat (4) @(posedge clk);
        rst = 1'b0;
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
