// YAP microcoded CPU (fpga-cpu m3): integer, load/store, jumps, CSRs.
// Verilog-2001. Control word: docs/cpu/design.md.
module yap_cpu (
    input              clk,
    input              rst,
    input              irq,
    input       [31:0] entry,
    input              init_p,
    input              init_ie,
    input       [31:0] init_ubase,
    input       [31:0] init_ulimit,
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
    localparam SEQ_NEXT        = 3'd0;
    localparam SEQ_DISPATCH    = 3'd1;
    localparam SEQ_GOTO        = 3'd2;
    localparam SEQ_HALT        = 3'd3;
    localparam SEQ_TRAP        = 3'd4;
    localparam SEQ_ERET        = 3'd5;
    localparam SEQ_SKIP_IF     = 3'd6;
    localparam SEQ_SKIP_UNLESS = 3'd7;
    localparam U_FETCH         = 8'h00;
    localparam U_ILLEGAL       = 8'h68;
    localparam TRAP_VEC        = 32'h80;
    localparam CAUSE_IRQ       = 8'd1;
    localparam CAUSE_PROT      = 8'd2;
    localparam CAUSE_SYS       = 8'd3;
    localparam CAUSE_COP       = 8'd6;
    localparam CAUSE_PRIV      = 8'd7;
    localparam CAUSE_ALIGN     = 8'd8;
    localparam CSR_STATUS      = 5'd0;
    localparam CSR_FLAGS       = 5'd1;
    localparam CSR_EPC         = 5'd2;
    localparam CSR_CAUSE       = 5'd3;
    localparam CSR_UBASE       = 5'd4;
    localparam CSR_ULIMIT      = 5'd5;

    reg [63:0] ucode [0:255];
    reg [7:0]  upc;
    reg [31:0] A, B, mar, mdr;
    reg [31:0] cause_r, epc_r, ubase_r, ulimit_r;
    reg        p, ie, te, pie, pp;
    reg        fl_z, fl_n, fl_c, fl_v;
    reg [1:0]  a_wait, b_wait, w_wait, mem_wait;
    reg [31:0] a_data, b_data, w_val;
    reg [4:0]  w_idx;
    reg [2:0]  pend_seq;
    reg [7:0]  pend_uimm;
    reg        pend_valid;
    reg        mem_write_r, mem_sext_r;
    reg [1:0]  mem_sz_r;
    reg [31:0] mosfet [0:12];
    reg [31:0] ic [0:15];
    reg [31:0] fregs [0:31];

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
    wire        cw_re    = cw[28];
    wire        cw_we    = cw[29];
    wire [1:0]  mem_sz   = cw[31:30];
    wire        we_flags = cw[32];
    wire        re_csr   = cw[33];
    wire        we_csr   = cw[34];
    wire        we_pc    = cw[35];
    wire [1:0]  idx_a    = cw[37:36];
    wire [1:0]  idx_b    = cw[39:38];
    wire        load_sext = cw[40];
    wire        irq_chk  = cw[41];
    wire [2:0]  flag_mode = cw[44:42];
    wire [2:0]  csr_idx  = cw[47:45];

    wire busy = (a_wait != 0) || (b_wait != 0) || (w_wait != 0) || (mem_wait != 0);
    wire executing = !rst && !halted && !busy && !pend_valid;

    wire [5:0]  ir_op  = ir[31:26];
    wire [4:0]  ir_rd  = ir[25:21];
    wire [4:0]  ir_rs  = ir[20:16];
    wire [4:0]  ir_rt  = ir[15:11];
    wire [4:0]  ir_sha = ir[10:6];
    wire [15:0] ir_imm = ir[15:0];
    wire [3:0]  ir_cond = ir[25:22];
    wire        jal_op = (ir_op == 6'd3);
    wire        cop1_op = (ir_op == 6'h11);
    wire        mfc1_op = cop1_op && (ir_rs == 5'd0);
    wire        mtc1_op = cop1_op && (ir_rs == 5'd4);
    wire [4:0]  wdst   = jal_op ? 5'd3 : ir_rd;

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
        reg [4:0] drs;
        begin
            dop = insn[31:26];
            dfn = insn[5:0];
            drs = insn[20:16];
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
                    6'h08: dispatch = 8'hb0;
                    6'h09: dispatch = 8'hb4;
                    6'h2d: dispatch = 8'ha0;
                    default: dispatch = U_ILLEGAL;
                endcase
            end else if (dop == 6'h0a)
                dispatch = 8'h9c;
            else if (dop == 6'h10) begin
                if (drs == 5'd0)
                    dispatch = 8'h8c;
                else if (drs == 5'd4)
                    dispatch = 8'h90;
                else
                    dispatch = U_ILLEGAL;
            end else if (dop == 6'h11) begin
                if (drs == 5'd0)
                    dispatch = 8'h94;
                else if (drs == 5'd4)
                    dispatch = 8'h98;
                else
                    dispatch = 8'ha4;
            end else begin
                case (dop)
                    6'h08: dispatch = 8'h4c;
                    6'h0c: dispatch = 8'h50;
                    6'h0d: dispatch = 8'h54;
                    6'h0e: dispatch = 8'h58;
                    6'h0f: dispatch = 8'h5c;
                    6'h09: dispatch = 8'h60;
                    6'h23: dispatch = 8'h6c;
                    6'h21: dispatch = 8'h70;
                    6'h20: dispatch = 8'h74;
                    6'h24: dispatch = 8'h78;
                    6'h25: dispatch = 8'h7c;
                    6'h2b: dispatch = 8'h80;
                    6'h29: dispatch = 8'h84;
                    6'h28: dispatch = 8'h88;
                    6'h02: dispatch = 8'ha8;
                    6'h03: dispatch = 8'hac;
                    6'h04: dispatch = 8'hb8;
                    default: dispatch = U_ILLEGAL;
                endcase
            end
        end
    endfunction

    function [2:0] bytes_of;
        input [1:0] sz;
        begin
            case (sz)
                2'd0: bytes_of = 3'd1;
                2'd1: bytes_of = 3'd2;
                default: bytes_of = 3'd4;
            endcase
        end
    endfunction

    function [31:0] ext_load;
        input [31:0] word;
        input [1:0]  off;
        input [1:0]  sz;
        input        sext;
        reg [31:0] raw;
        begin
            case (sz)
                2'd0: begin
                    raw = (word >> (8 * off)) & 32'hff;
                    if (sext && raw[7])
                        raw = raw | 32'hffffff00;
                end
                2'd1: begin
                    raw = (word >> (8 * off)) & 32'hffff;
                    if (sext && raw[15])
                        raw = raw | 32'hffff0000;
                end
                default: raw = word;
            endcase
            ext_load = raw;
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
    wire [1:0]  latw = bank_lat(wdst);

    wire [31:0] A_use = (executing && re_a && lata == 2'd0) ? rda : A;
    wire [31:0] B_use = (executing && re_b && latb == 2'd0) ? rdb : B;

    wire [4:0] csr_sel = (csr_idx == 3'd0) ? ir_rt :
                         (csr_idx == 3'd1) ? CSR_STATUS :
                         (csr_idx == 3'd2) ? CSR_FLAGS :
                         (csr_idx == 3'd3) ? CSR_EPC :
                         (csr_idx == 3'd4) ? CSR_CAUSE :
                         (csr_idx == 3'd5) ? CSR_UBASE : CSR_ULIMIT;

    reg [31:0] csr_rd;
    always @(*) begin
        case (csr_sel)
            CSR_STATUS: csr_rd = {{22{1'b0}}, pp, pie, 5'b0, te, p, ie};
            CSR_FLAGS:  csr_rd = {28'd0, fl_v, fl_c, fl_n, fl_z};
            CSR_EPC:    csr_rd = epc_r;
            CSR_CAUSE:  csr_rd = cause_r;
            CSR_UBASE:  csr_rd = ubase_r;
            CSR_ULIMIT: csr_rd = ulimit_r;
            default:    csr_rd = 32'd0;
        endcase
    end
    wire [31:0] csr_use = (executing && re_csr) ? csr_rd : 32'd0;

    reg [31:0] f_rd;
    always @(*)
        f_rd = fregs[ir_rt];

    wire [31:0] sextimm = {{16{ir_imm[15]}}, ir_imm};
    wire [31:0] zextimm = {16'd0, ir_imm};
    wire [31:0] pc4     = pc + 32'd4;
    wire [31:0] jtgt    = (pc4 & 32'hF0000000) | {ir[25:0], 2'b00};
    wire [31:0] broff   = {{8{ir[21]}}, ir[21:0], 2'b00};

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
            3'd4: a_mux = csr_use;
            3'd5: a_mux = 32'd0;
            3'd6: a_mux = 32'd4;
            3'd7: a_mux = jtgt;
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
            3'd7: b_mux = broff;
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

    wire [31:0] wb_val = mfc1_op ? f_rd : aluout;

    wire add_c = ({1'b0, a_mux} + {1'b0, b_mux}) >> 32;
    wire add_v = (a_mux[31] == b_mux[31]) && (aluout[31] != a_mux[31]);
    wire sub_c = a_mux < b_mux;
    wire sub_v = (a_mux[31] != b_mux[31]) && (aluout[31] != a_mux[31]);

    wire [31:0] mar_use = (dst == 3'd4) ? aluout : mar;
    wire [2:0]  acc_sz  = bytes_of(mem_sz);
    wire        misalign = (mem_sz == 2'd1 && mar_use[0]) || (mem_sz == 2'd2 && mar_use[1:0] != 2'd0);
    wire [31:0] acc_last = mar_use + {29'd0, acc_sz} - 32'd1;
    wire        in_win   = (mar_use >= ubase_r) && (acc_last < ulimit_r);
    wire        pc_in_win = (pc >= ubase_r) && ((pc + 32'd3) < ulimit_r);

    reg taken;
    always @(*) begin
        case (ir_cond)
            4'd0: taken = fl_z;
            4'd1: taken = ~fl_z;
            4'd2: taken = fl_n ^ fl_v;
            4'd3: taken = ~(fl_n ^ fl_v);
            4'd4: taken = fl_c;
            4'd5: taken = ~fl_c;
            4'd6: taken = fl_z | (fl_n ^ fl_v);
            4'd7: taken = ~(fl_z | (fl_n ^ fl_v));
            4'd8: taken = fl_n;
            4'd9: taken = ~fl_n;
            default: taken = 1'b0;
        endcase
    end

    assign mem_addr  = mar;
    assign mem_re    = executing && cw_re;
    assign mem_we    = !rst && !halted && (mem_wait == 2'd1) && mem_write_r;
    assign mem_wdata = mdr;
    assign mem_size  = bytes_of(mem_sz_r);
    assign flags     = {28'd0, fl_v, fl_c, fl_n, fl_z};
    assign status    = {{22{1'b0}}, pp, pie, 5'b0, te, p, ie};
    assign cause_o   = cause_r;
    assign epc       = epc_r;
    assign ubase     = ubase_r;
    assign ulimit    = ulimit_r;

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

    task do_trap;
        input [7:0] code;
        begin
            cause_r <= {24'd0, code};
            pie <= ie;
            pp <= p;
            p <= 1'b1;
            ie <= 1'b0;
            if (code == CAUSE_SYS)
                epc_r <= pc + 32'd4;
            else
                epc_r <= pc;
            pc <= TRAP_VEC;
            upc <= U_FETCH;
            pend_valid <= 1'b0;
            a_wait <= 0; b_wait <= 0; w_wait <= 0; mem_wait <= 0;
            mem_write_r <= 1'b0;
        end
    endtask

    task apply_seq;
        input [2:0] s;
        input [7:0] u;
        begin
            case (s)
                SEQ_NEXT:     upc <= upc + 8'd1;
                SEQ_DISPATCH: upc <= dispatch(we_ir ? mdr : ir);
                SEQ_GOTO:     upc <= u;
                SEQ_HALT:     halted <= 1'b1;
                SEQ_TRAP:     do_trap(u);
                SEQ_ERET: begin
                    ie <= pie;
                    p <= pp;
                    pc <= epc_r;
                    upc <= U_FETCH;
                end
                SEQ_SKIP_IF:     upc <= upc + (taken ? 8'd2 : 8'd1);
                SEQ_SKIP_UNLESS: upc <= upc + (taken ? 8'd1 : 8'd2);
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
        for (i = 0; i < 32; i = i + 1)
            fregs[i] = 32'd0;
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
            ubase_r    <= init_ubase;
            ulimit_r   <= init_ulimit;
            p          <= init_p;
            ie         <= init_ie;
            te         <= 1'b0;
            pie        <= 1'b0;
            pp         <= 1'b1;
            fl_z <= 1'b0; fl_n <= 1'b0; fl_c <= 1'b0; fl_v <= 1'b0;
            a_wait <= 0; b_wait <= 0; w_wait <= 0; mem_wait <= 0;
            pend_valid <= 1'b0;
            mem_write_r <= 1'b0;
            mem_sext_r <= 1'b0;
            mem_sz_r <= 2'd2;
            for (i = 0; i < 13; i = i + 1)
                mosfet[i] <= 32'd0;
            for (i = 0; i < 16; i = i + 1)
                ic[i] <= 32'd0;
            for (i = 0; i < 32; i = i + 1)
                fregs[i] <= 32'd0;
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
                    if (mem_wait == 2'd1) begin
                        if (!mem_write_r)
                            mdr <= ext_load(mem_rdata, mar[1:0], mem_sz_r, mem_sext_r);
                        mem_write_r <= 1'b0;
                    end
                end
                if ((a_wait <= 1) && (b_wait <= 1) && (w_wait <= 1) && (mem_wait <= 1) && pend_valid) begin
                    pend_valid <= 1'b0;
                    apply_seq(pend_seq, pend_uimm);
                end
            end else if (pend_valid) begin
                pend_valid <= 1'b0;
                apply_seq(pend_seq, pend_uimm);
            end else begin
                if (irq_chk && ie && irq)
                    do_trap(CAUSE_IRQ);
                else if (irq_chk && (pc[1:0] != 2'd0))
                    do_trap(CAUSE_ALIGN);
                else if (irq_chk && !p && !pc_in_win)
                    do_trap(CAUSE_PROT);
                else if (re_csr && !p && (csr_sel != CSR_STATUS) && (csr_sel != CSR_FLAGS))
                    do_trap(CAUSE_PRIV);
                else if (seq == SEQ_ERET && !p)
                    do_trap(CAUSE_PRIV);
                else if (cw_re && misalign)
                    do_trap(CAUSE_ALIGN);
                else if (cw_we && misalign)
                    do_trap(CAUSE_ALIGN);
                else if ((cw_re || cw_we) && !p && !in_win)
                    do_trap(CAUSE_PROT);
                else if (we_csr && !p && !mtc1_op)
                    do_trap(CAUSE_PRIV);
                else if (we_csr && !mtc1_op && (csr_sel == CSR_STATUS) && aluout[2])
                    do_trap(CAUSE_PRIV);
                else begin
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
                    if (dst == 3'd2)
                        pc <= aluout;
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
                    if (we_rf && wdst > 5'd2) begin
                        if (latw == 2'd0)
                            write_gpr(wdst, wb_val);
                        else begin
                            w_idx <= wdst;
                            w_val <= wb_val;
                            w_wait <= latw;
                        end
                    end
                    if (we_csr) begin
                        if (mtc1_op)
                            fregs[ir_rt] <= A;
                        else case (csr_sel)
                            CSR_STATUS: begin
                                ie <= aluout[0];
                                p <= aluout[1];
                                te <= 1'b0;
                                pie <= aluout[8];
                                pp <= aluout[9];
                            end
                            CSR_FLAGS: begin
                                fl_z <= aluout[0];
                                fl_n <= aluout[1];
                                fl_c <= aluout[2];
                                fl_v <= aluout[3];
                            end
                            CSR_EPC:    epc_r <= aluout;
                            CSR_CAUSE:  cause_r <= aluout;
                            CSR_UBASE:  ubase_r <= aluout;
                            CSR_ULIMIT: ulimit_r <= aluout;
                            default: ;
                        endcase
                    end
                    if (cw_re || cw_we) begin
                        mem_wait    <= 2'd1;
                        mem_write_r <= cw_we;
                        mem_sext_r  <= load_sext;
                        mem_sz_r    <= mem_sz;
                        pend_valid  <= 1'b1;
                        pend_seq    <= seq;
                        pend_uimm   <= uimm;
                    end else if ((re_a && lata != 0) || (re_b && latb != 0) || (we_rf && wdst > 5'd2 && latw != 0)) begin
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
