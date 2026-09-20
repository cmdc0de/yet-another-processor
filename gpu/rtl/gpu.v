// yap_gpu: YAP-160 backbuffer + MMIO fill. Verilog-2001. RGB888 0x00RRGGBB.
module yap_gpu (
    input         clk,
    input         rst,
    input         we,
    input  [7:0]  addr,
    input  [31:0] wdata
);
    localparam WIDTH  = 160;
    localparam HEIGHT = 120;
    localparam NPX    = 19200;

    reg [31:0] fb [0:NPX-1];
    reg [31:0] color;
    reg [31:0] x0;
    reg [31:0] y0;
    reg [31:0] x1;
    reg [31:0] y1;
    integer    i;
    integer    x;
    integer    y;
    integer    xs;
    integer    xe;
    integer    ys;
    integer    ye;

    always @(posedge clk) begin
        if (rst) begin
            color <= 32'h0;
            x0 <= 32'h0;
            y0 <= 32'h0;
            x1 <= 32'h0;
            y1 <= 32'h0;
            for (i = 0; i < NPX; i = i + 1)
                fb[i] <= 32'h00000000;
        end else if (we) begin
            if (addr == 8'h04)
                color <= wdata;
            else if (addr == 8'h08)
                x0 <= wdata;
            else if (addr == 8'h0c)
                y0 <= wdata;
            else if (addr == 8'h10)
                x1 <= wdata;
            else if (addr == 8'h14)
                y1 <= wdata;
            else if (addr == 8'h00 && wdata == 32'd1) begin
                xs = (x0 > WIDTH)  ? WIDTH  : x0;
                xe = (x1 > WIDTH)  ? WIDTH  : x1;
                ys = (y0 > HEIGHT) ? HEIGHT : y0;
                ye = (y1 > HEIGHT) ? HEIGHT : y1;
                for (y = 0; y < HEIGHT; y = y + 1)
                    for (x = 0; x < WIDTH; x = x + 1)
                        if (y >= ys && y < ye && x >= xs && x < xe)
                            fb[y * WIDTH + x] <= color;
            end
        end
    end
endmodule
