// yap_fpu: COP1 file f0-f31. Verilog-2001. IEEE-754 binary32.
module yap_fpu (
    input clk,
    input rst
);
    // f0-f31: IEEE-754 binary32 words
    reg [31:0] f [0:31];
    integer    i;

    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 32; i = i + 1)
                f[i] <= 32'h00000000;
        end
    end
endmodule
