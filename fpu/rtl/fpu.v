// yap_fpu: COP1 file f0-f31 + add.s/sub.s/mul.s/div.s. Verilog-2001.
// IEEE-754 binary32. Invalid → qNaN 0x7FC00000. Div-by-zero → signed inf.
module yap_fpu (
    input        clk,
    input        rst,
    input        we,
    input [4:0]  fd,
    input [4:0]  fs,
    input [4:0]  ft,
    input [5:0]  funct
);
    localparam [31:0] QNAN = 32'h7FC00000;
    localparam [5:0]  F_ADD = 6'd0;
    localparam [5:0]  F_SUB = 6'd1;
    localparam [5:0]  F_MUL = 6'd2;
    localparam [5:0]  F_DIV = 6'd3;

    // f0-f31: IEEE-754 binary32 words
    reg [31:0] f [0:31];
    integer    i;
    reg [31:0] a;
    reg [31:0] b;
    reg [31:0] y;

    function is0;
        input [31:0] x;
        begin
            is0 = (x[30:0] == 31'b0);
        end
    endfunction

    function real bits32_to_real;
        input [31:0] x;
        reg   [63:0] d;
        integer      ue;
        begin
            if (x[30:0] == 31'b0)
                d = {x[31], 63'b0};
            else if (x[30:23] == 8'hff)
                d = {x[31], 11'h7ff, |x[22:0], x[21:0], 29'b0};
            else if (x[30:23] == 8'h00)
                d = {x[31], 63'b0};
            else begin
                ue = x[30:23] + 896;
                d = {x[31], ue[10:0], x[22:0], 29'b0};
            end
            bits32_to_real = $bitstoreal(d);
        end
    endfunction

    function [31:0] real_to_bits32;
        input real r;
        reg [63:0] d;
        reg        sign;
        integer    exp64;
        integer    exp32;
        reg [51:0] frac64;
        reg [22:0] mant;
        reg        round_bit;
        reg        sticky;
        reg        lsb;
        begin
            d = $realtobits(r);
            sign = d[63];
            exp64 = d[62:52];
            frac64 = d[51:0];
            if (exp64 == 2047) begin
                if (frac64 == 0)
                    real_to_bits32 = {sign, 8'hff, 23'b0};
                else
                    real_to_bits32 = QNAN;
            end else if (exp64 == 0) begin
                real_to_bits32 = {sign, 31'b0};
            end else begin
                exp32 = exp64 - 1023 + 127;
                if (exp32 >= 255)
                    real_to_bits32 = {sign, 8'hff, 23'b0};
                else if (exp32 <= 0)
                    real_to_bits32 = {sign, 31'b0};
                else begin
                    mant = frac64[51:29];
                    round_bit = frac64[28];
                    sticky = |frac64[27:0];
                    lsb = frac64[29];
                    if (round_bit && (sticky || lsb)) begin
                        {round_bit, mant} = {1'b0, mant} + 1'b1;
                        if (round_bit) begin
                            mant = 23'b0;
                            exp32 = exp32 + 1;
                        end
                    end
                    if (exp32 >= 255)
                        real_to_bits32 = {sign, 8'hff, 23'b0};
                    else
                        real_to_bits32 = {sign, exp32[7:0], mant};
                end
            end
        end
    endfunction

    always @(posedge clk) begin
        if (rst) begin
            for (i = 0; i < 32; i = i + 1)
                f[i] <= 32'h00000000;
        end else if (we) begin
            a = f[fs];
            b = f[ft];
            y = 32'h0;
            if (funct == F_ADD)
                y = real_to_bits32(bits32_to_real(a) + bits32_to_real(b));
            else if (funct == F_SUB)
                y = real_to_bits32(bits32_to_real(a) - bits32_to_real(b));
            else if (funct == F_MUL)
                y = real_to_bits32(bits32_to_real(a) * bits32_to_real(b));
            else if (funct == F_DIV) begin
                if (is0(a) && is0(b))
                    y = QNAN;
                else if (is0(b))
                    y = {a[31], 8'hff, 23'b0};
                else
                    y = real_to_bits32(bits32_to_real(a) / bits32_to_real(b));
            end
            f[fd] <= y;
        end
    end
endmodule
