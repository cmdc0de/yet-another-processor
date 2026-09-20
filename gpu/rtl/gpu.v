// yap_gpu: YAP-160 backbuffer. Verilog-2001. RGB888 0x00RRGGBB.
// 160 x 120, GPU-local fb[]. MMIO fill is later (GPU-007).
module yap_gpu (
    input clk,
    input rst
);
    localparam WIDTH  = 160;
    localparam HEIGHT = 120;
    localparam NPX    = 19200;

    reg [31:0] fb [0:NPX-1];
    integer    i;

    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < NPX; i = i + 1)
                fb[i] <= 32'h00000000;
        end
    end
endmodule
