// YAP microcoded CPU (fpga-cpu m2): fetch, integer ALU, split RF, halt.
// Verilog-2001. Control word: docs/cpu/design.md.
module yap_cpu (
    input              clk,
    input              rst,
    input              irq,
    input       [31:0] entry,
    input       [31:0] mem_rdata,
    output      [31:0] mem_addr,
    output             mem_re,
    output             mem_we,
    output      [2:0]  mem_size,
    output      [31:0] mem_wdata,
    output reg         halted,
    output reg  [31:0] pc,
    output reg  [31:0] ir,
    output reg  [31:0] cycles,
    output      [31:0] flags,
    output      [31:0] status,
    output      [31:0] cause_o,
    output      [31:0] epc,
    output      [31:0] ubase,
    output      [31:0] ulimit,
    output     [1023:0] gprs
);
    localparam SEQ_NEXT     = 3'd0;
    localparam SEQ_DISPATCH = 3'd1;
    localparam SEQ_GOTO     = 3'd2;
    localparam SEQ_HALT     = 3'd3;
    localparam SEQ_TRAP     = 3'd4;
    localparam U_FETCH      = 8'h00;
    localparam U_ILLEGAL    = 8'h68;
    localparam TRAP_VEC     = 32'h80;
    localparam CAUSE_ALIGN  = 32'd8;

    reg [63:0] ucode [0:255];
    reg [7:0]  upc;
    reg [31:0] A, B, mar, mdr;
    reg [31:0] cause_r, epc_r;
    reg        p, ie;
    reg        fl_z, fl_n, fl_c, fl_v;
    reg [1:0]  a_wait, b_wait, w_wait, mem_wait;
    reg [31:0] a_data, b_data, w_val;
    reg [4:0]  w_idx;
    reg [2:0]  pend_seq;
    reg [7:0]  pend_uimm;
    reg        pend_valid;
    reg [31:0] mosfet [0:12];
    reg [31:0] ic [0:15];

    wire [63:0] cw = ucode[upc];
    wire [2:0]  seq      = cw[2:0];
    wire [7:0]  uimm     = cw[10:3];
    wire [3:0]  alu_op   = cw[14:11];
    wire [2:0]  a_sel    = cw[17:15];
    wire [2:0]  b_sel    = cw[20:18];
    wire [2:0]  dst      = cw[23:21];
    wire        re_a     = cw[24];
    wire        re_b     = cw[25];
    wire        we_rf    = cw[26];
    wire        we_ir    = cw[27];
    wire [1:0]  mem_sz   = cw[31:30];
    wire        we_flags = cw[32];
    wire        we_pc    = cw[35];
    wire [1:0]  idx_a    = cw[37:36];
    wire [1:0]  idx_b    = cw[39:38];
    wire        irq_chk  = cw[41];
    wire [2:0]  flag_mode = cw[44:42];

    wire busy = (a_wait != 0) || (b_wait != 0) || (w_wait != 0) || (mem_wait != 0);
    wire executing = !rst && !halted && !busy && !pend_valid;

    wire [4:0]  ir_rd  = ir[25:21];
    wire [4:0]  ir_rs  = ir[20:16];
    wire [4:0]  ir_rt  = ir[15:11];
    wire [4:0]  ir_sha = ir[10:6];
    wire [15:0] ir_imm = ir[15:0];

    function [1:0] bank_lat;
        input [4:0] idx;
        begin
            if (idx <= 5'd2)
                bank_lat = 2'd0;
            else if (idx <= 5'd15)
                bank_lat = 2'd1;
            else
                bank_lat = 2'd2;
        end
    endfunction

    function [7:0] dispatch;
        input [31:0] insn;
        reg [5:0] dop, dfn;
        begin
            dop = insn[31:26];
            dfn = insn[5:0];
            if (dop == 6'd0) begin
                case (dfn)
                    6'h20: dispatch = 8'h08;
                    6'h22: dispatch = 8'h0c;
                    6'h24: dispatch = 8'h10;
                    6'h25: dispatch = 8'h14;
                    6'h26: dispatch = 8'h18;
                    6'h27: dispatch = 8'h1c;
                    6'h00: dispatch = 8'h20;
                    6'h02: dispatch = 8'h24;
                    6'h03: dispatch = 8'h28;
                    6'h04: dispatch = 8'h2c;
                    6'h06: dispatch = 8'h30;
                    6'h07: dispatch = 8'h34;
                    6'h18: dispatch = 8'h38;
                    6'h1a: dispatch = 8'h3c;
                    6'h2a: dispatch = 8'h40;
                    6'h28: dispatch = 8'h44;
                    6'h29: dispatch = 8'h48;
                    6'h2c: dispatch = 8'h64;
                    default: dispatch = U_ILLEGAL;
                endcase
            end else begin
                case (dop)
                    6'h08: dispatch = 8'h4c;
                    6'h0c: dispatch = 8'h50;
                    6'h0d: dispatch = 8'h54;
                    6'h0e: dispatch = 8'h58;
                    6'h0f: dispatch = 8'h5c;
                    6'h09: dispatch = 8'h60;
                    default: dispatch = U_ILLEGAL;
                endcase
            end
        end
    endfunction

    reg  [4:0]  idxa, idxb;
    reg  [31:0] rda, rdb;
    always @(*) begin
        case (idx_a)
            2'd0: idxa = ir_rs;
            2'd1: idxa = ir_rt;
            2'd2: idxa = ir_rd;
            default: idxa = 5'd3;
        endcase
        case (idx_b)
            2'd0: idxb = ir_rs;
            2'd1: idxb = ir_rt;
            2'd2: idxb = ir_rd;
            default: idxb = 5'd3;
        endcase
        if (idxa == 5'd0)
            rda = 32'd0;
        else if (idxa == 5'd1)
            rda = 32'd1;
        else if (idxa == 5'd2)
            rda = 32'hffffffff;
        else if (idxa <= 5'd15)
            rda = mosfet[idxa - 5'd3];
        else
            rda = ic[idxa - 5'd16];
        if (idxb == 5'd0)
            rdb = 32'd0;
        else if (idxb == 5'd1)
            rdb = 32'd1;
        else if (idxb == 5'd2)
            rdb = 32'hffffffff;
        else if (idxb <= 5'd15)
            rdb = mosfet[idxb - 5'd3];
        else
            rdb = ic[idxb - 5'd16];
    end
    wire [1:0]  lata = bank_lat(idxa);
    wire [1:0]  latb = bank_lat(idxb);
    wire [1:0]  latw = bank_lat(ir_rd);

    wire [31:0] A_use = (executing && re_a && lata == 2'd0) ? rda : A;
    wire [31:0] B_use = (executing && re_b && latb == 2'd0) ? rdb : B;

    wire [31:0] sextimm = {{16{ir_imm[15]}}, ir_imm};
    wire [31:0] zextimm = {16'd0, ir_imm};

    reg [31:0] a_mux, b_mux, aluout;
    reg        shift_c;
    reg signed [31:0] a_signed;
    integer gi;

    always @(*) begin
        case (a_sel)
            3'd0: a_mux = A_use;
            3'd1: a_mux = pc;
            3'd2: a_mux = epc_r;
            3'd3: a_mux = mdr;
            3'd5: a_mux = 32'd0;
            3'd6: a_mux = 32'd4;
            default: a_mux = 32'd0;
        endcase
        case (b_sel)
            3'd0: b_mux = B_use;
            3'd1: b_mux = sextimm;
            3'd2: b_mux = zextimm;
            3'd3: b_mux = {27'd0, ir_sha};
            3'd4: b_mux = {27'd0, ir_rt};
            3'd5: b_mux = 32'd4;
            3'd6: b_mux = 32'd0;
            default: b_mux = 32'd0;
        endcase
        shift_c = 1'b0;
        a_signed = a_mux;
        case (alu_op)
            4'd0: aluout = a_mux + b_mux;
            4'd1: aluout = a_mux - b_mux;
            4'd2: aluout = a_mux & b_mux;
            4'd3: aluout = a_mux | b_mux;
            4'd4: aluout = a_mux ^ b_mux;
            4'd5: aluout = ~a_mux;
            4'd6: begin
                if (b_mux[4:0] == 5'd0) begin
                    aluout = a_mux;
                    shift_c = 1'b0;
                end else begin
                    aluout = a_mux << b_mux[4:0];
                    shift_c = a_mux[32 - b_mux[4:0]];
                end
            end
            4'd7: begin
                if (b_mux[4:0] == 5'd0) begin
                    aluout = a_mux;
                    shift_c = 1'b0;
                end else begin
                    aluout = a_mux >> b_mux[4:0];
                    shift_c = a_mux[b_mux[4:0] - 5'd1];
                end
            end
            4'd8: begin
                if (b_mux[4:0] == 5'd0) begin
                    aluout = a_mux;
                    shift_c = 1'b0;
                end else begin
                    aluout = a_signed >>> b_mux[4:0];
                    shift_c = a_mux[b_mux[4:0] - 5'd1];
                end
            end
            4'd9: aluout = a_mux * b_mux;
            4'd10: begin
                if (b_mux == 32'd0)
                    aluout = 32'd0;
                else
                    aluout = a_mux / b_mux;
            end
            4'd11: aluout = a_mux;
            4'd12: aluout = b_mux;
            4'd13: aluout = {ir_imm, 16'd0};
            default: aluout = a_mux;
        endcase
    end

    wire add_c = ({1'b0, a_mux} + {1'b0, b_mux}) >> 32;
    wire add_v = (a_mux[31] == b_mux[31]) && (aluout[31] != a_mux[31]);
    wire sub_c = a_mux < b_mux;
    wire sub_v = (a_mux[31] != b_mux[31]) && (aluout[31] != a_mux[31]);

    assign mem_addr  = mar;
    assign mem_re    = executing && cw[28];
    assign mem_we    = 1'b0;
    assign mem_wdata = 32'd0;
    assign mem_size  = (mem_sz == 2'd2) ? 3'd4 : (mem_sz == 2'd1) ? 3'd2 : 3'd1;
    assign flags     = {28'd0, fl_v, fl_c, fl_n, fl_z};
    assign status    = {30'd0, p, ie};
    assign cause_o   = cause_r;
    assign epc       = epc_r;
    assign ubase     = 32'd0;
    assign ulimit    = 32'h10000;

    reg [1023:0] gprs_r;
    assign gprs = gprs_r;
    always @(*) begin
        gprs_r[31:0] = 32'd0;
        gprs_r[63:32] = 32'd1;
        gprs_r[95:64] = 32'hffffffff;
        for (gi = 3; gi < 16; gi = gi + 1)
            gprs_r[32*gi +: 32] = mosfet[gi-3];
        for (gi = 16; gi < 32; gi = gi + 1)
            gprs_r[32*gi +: 32] = ic[gi-16];
    end

    task apply_seq;
        input [2:0] s;
        input [7:0] u;
        begin
            case (s)
                SEQ_NEXT:     upc <= upc + 8'd1;
                SEQ_DISPATCH: upc <= dispatch(we_ir ? mdr : ir);
                SEQ_GOTO:     upc <= u;
                SEQ_HALT:     halted <= 1'b1;
                SEQ_TRAP: begin
                    cause_r <= {24'd0, u};
                    p <= 1'b1;
                    ie <= 1'b0;
                    epc_r <= pc;
                    pc <= TRAP_VEC;
                    upc <= U_FETCH;
                end
                default: upc <= upc + 8'd1;
            endcase
        end
    endtask

    task write_gpr;
        input [4:0] idx;
        input [31:0] val;
        begin
            if (idx > 5'd2 && idx <= 5'd15)
                mosfet[idx-5'd3] <= val;
            else if (idx >= 5'd16)
                ic[idx-5'd16] <= val;
        end
    endtask

    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1)
            ucode[i] = 64'd0;
        for (i = 0; i < 13; i = i + 1)
            mosfet[i] = 32'd0;
        for (i = 0; i < 16; i = i + 1)
            ic[i] = 32'd0;
    end

    always @(posedge clk) begin
        if (rst) begin
            halted     <= 1'b0;
            pc         <= entry;
            ir         <= 32'd0;
            cycles     <= 32'd0;
            upc        <= U_FETCH;
            A          <= 32'd0;
            B          <= 32'd0;
            mar        <= 32'd0;
            mdr        <= 32'd0;
            cause_r    <= 32'd0;
            epc_r      <= 32'd0;
            p          <= 1'b1;
            ie         <= 1'b0;
            fl_z <= 1'b0; fl_n <= 1'b0; fl_c <= 1'b0; fl_v <= 1'b0;
            a_wait <= 0; b_wait <= 0; w_wait <= 0; mem_wait <= 0;
            pend_valid <= 1'b0;
            for (i = 0; i < 13; i = i + 1)
                mosfet[i] <= 32'd0;
            for (i = 0; i < 16; i = i + 1)
                ic[i] <= 32'd0;
        end else if (halted) begin
        end else begin
            cycles <= cycles + 32'd1;
            if (busy) begin
                if (a_wait != 0) begin
                    a_wait <= a_wait - 2'd1;
                    if (a_wait == 2'd1)
                        A <= a_data;
                end
                if (b_wait != 0) begin
                    b_wait <= b_wait - 2'd1;
                    if (b_wait == 2'd1)
                        B <= b_data;
                end
                if (w_wait != 0) begin
                    w_wait <= w_wait - 2'd1;
                    if (w_wait == 2'd1)
                        write_gpr(w_idx, w_val);
                end
                if (mem_wait != 0) begin
                    mem_wait <= mem_wait - 2'd1;
                    if (mem_wait == 2'd1)
                        mdr <= mem_rdata;
                end
                if ((a_wait <= 1) && (b_wait <= 1) && (w_wait <= 1) && (mem_wait <= 1) && pend_valid) begin
                    pend_valid <= 1'b0;
                    apply_seq(pend_seq, pend_uimm);
                end
            end else if (pend_valid) begin
                pend_valid <= 1'b0;
                apply_seq(pend_seq, pend_uimm);
            end else begin
                if (irq_chk && (pc[1:0] != 2'd0)) begin
                    cause_r <= CAUSE_ALIGN;
                    p <= 1'b1;
                    ie <= 1'b0;
                    epc_r <= pc;
                    pc <= TRAP_VEC;
                    upc <= U_FETCH;
                end else begin
                    if (re_a) begin
                        a_data <= rda;
                        if (lata == 2'd0)
                            A <= rda;
                        else
                            a_wait <= lata;
                    end
                    if (re_b) begin
                        b_data <= rdb;
                        if (latb == 2'd0)
                            B <= rdb;
                        else
                            b_wait <= latb;
                    end
                    if (dst == 3'd4)
                        mar <= aluout;
                    if (dst == 3'd5)
                        mdr <= aluout;
                    if (we_ir)
                        ir <= mdr;
                    if (we_pc)
                        pc <= aluout;
                    if (we_flags) begin
                        case (flag_mode)
                            3'd0: begin
                                fl_z <= (aluout == 32'd0);
                                fl_n <= aluout[31];
                                fl_c <= add_c;
                                fl_v <= add_v;
                            end
                            3'd1: begin
                                fl_z <= (aluout == 32'd0);
                                fl_n <= aluout[31];
                                fl_c <= sub_c;
                                fl_v <= sub_v;
                            end
                            3'd3: begin
                                fl_z <= (aluout == 32'd0);
                                fl_n <= aluout[31];
                                fl_c <= shift_c;
                                fl_v <= 1'b0;
                            end
                            3'd4: begin
                                fl_z <= (aluout == 32'd0);
                                fl_n <= 1'b0;
                                fl_c <= 1'b0;
                                fl_v <= 1'b0;
                            end
                            default: begin
                                fl_z <= (aluout == 32'd0);
                                fl_n <= aluout[31];
                                fl_c <= 1'b0;
                                fl_v <= 1'b0;
                            end
                        endcase
                    end
                    if (we_rf && ir_rd > 5'd2) begin
                        if (latw == 2'd0)
                            write_gpr(ir_rd, aluout);
                        else begin
                            w_idx <= ir_rd;
                            w_val <= aluout;
                            w_wait <= latw;
                        end
                    end
                    if (cw[28]) begin
                        mem_wait   <= 2'd1;
                        pend_valid <= 1'b1;
                        pend_seq   <= seq;
                        pend_uimm  <= uimm;
                    end else if ((re_a && lata != 0) || (re_b && latb != 0) || (we_rf && ir_rd > 5'd2 && latw != 0)) begin
                        pend_valid <= 1'b1;
                        pend_seq   <= seq;
                        pend_uimm  <= uimm;
                    end else if (seq == SEQ_DISPATCH)
                        upc <= dispatch(we_ir ? mdr : ir);
                    else
                        apply_seq(seq, uimm);
                end
            end
        end
    end
endmodule
