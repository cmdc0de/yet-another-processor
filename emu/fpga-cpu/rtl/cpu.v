// YAP microcoded CPU stub (fpga-cpu m1): fetch + halt.
// Verilog-2001. Control word: docs/cpu/design.md.
module yap_cpu (
    input             clk,
    input             rst,
    input             irq,
    input      [31:0] entry,
    input      [31:0] mem_rdata,
    output     [31:0] mem_addr,
    output            mem_re,
    output            mem_we,
    output     [2:0]  mem_size,
    output     [31:0] mem_wdata,
    output reg        halted,
    output reg [31:0] pc,
    output reg [31:0] ir,
    output reg [31:0] cycles,
    output     [31:0] flags,
    output     [31:0] status,
    output     [31:0] cause_o,
    output     [31:0] epc,
    output     [31:0] ubase,
    output     [31:0] ulimit
);
    localparam SEQ_NEXT     = 3'd0;
    localparam SEQ_DISPATCH = 3'd1;
    localparam SEQ_GOTO     = 3'd2;
    localparam SEQ_HALT     = 3'd3;
    localparam SEQ_TRAP     = 3'd4;
    localparam ALU_PASS_A   = 4'd11;
    localparam A_PC         = 3'd1;
    localparam DST_MAR      = 3'd4;
    localparam U_FETCH      = 8'h00;
    localparam U_HALT       = 8'h64;
    localparam U_ILLEGAL    = 8'h68;
    localparam FUNCT_HALT   = 6'h2c;
    localparam CAUSE_ALIGN  = 32'd8;
    localparam CAUSE_PRIV   = 32'd7;
    localparam TRAP_VEC     = 32'h80;

    reg [63:0] ucode [0:255];
    reg [7:0]  upc;
    reg [31:0] mar;
    reg [31:0] mdr;
    reg [31:0] cause_r;
    reg [31:0] epc_r;
    reg        p;
    reg        ie;
    reg [1:0]  mem_wait;
    reg [2:0]  pend_seq;
    reg [7:0]  pend_uimm;
    reg        pend_valid;

    wire [63:0] cw = ucode[upc];
    wire [2:0]  seq     = cw[2:0];
    wire [7:0]  uimm    = cw[10:3];
    wire [3:0]  alu_op  = cw[14:11];
    wire [2:0]  a_sel   = cw[17:15];
    wire [2:0]  dst     = cw[23:21];
    wire        we_ir   = cw[27];
    wire        cw_re   = cw[28];
    wire [1:0]  mem_sz  = cw[31:30];
    wire        irq_chk = cw[41];

    wire executing = !rst && !halted && (mem_wait == 2'd0) && !pend_valid;
    wire [31:0] a_mux = (a_sel == A_PC) ? pc : 32'd0;
    wire [31:0] aluout = (alu_op == ALU_PASS_A) ? a_mux : a_mux;

    assign mem_addr  = mar;
    assign mem_re    = executing && cw_re;
    assign mem_we    = 1'b0;
    assign mem_wdata = 32'd0;
    assign mem_size  = (mem_sz == 2'd2) ? 3'd4 : (mem_sz == 2'd1) ? 3'd2 : 3'd1;
    assign flags     = 32'd0;
    assign status    = {30'd0, p, ie};
    assign cause_o   = cause_r;
    assign epc       = epc_r;
    assign ubase     = 32'd0;
    assign ulimit    = 32'h10000;

    function [7:0] dispatch;
        input [31:0] insn;
        begin
            if (insn[31:26] == 6'd0 && insn[5:0] == FUNCT_HALT)
                dispatch = U_HALT;
            else
                dispatch = U_ILLEGAL;
        end
    endfunction

    task apply_seq;
        input [2:0] s;
        input [7:0] u;
        begin
            case (s)
                SEQ_NEXT:     upc <= upc + 8'd1;
                SEQ_DISPATCH: upc <= dispatch(ir);
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

    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1)
            ucode[i] = 64'd0;
    end

    always @(posedge clk) begin
        if (rst) begin
            halted     <= 1'b0;
            pc         <= entry;
            ir         <= 32'd0;
            cycles     <= 32'd0;
            upc        <= U_FETCH;
            mar        <= 32'd0;
            mdr        <= 32'd0;
            cause_r    <= 32'd0;
            epc_r      <= 32'd0;
            p          <= 1'b1;
            ie         <= 1'b0;
            mem_wait   <= 2'd0;
            pend_valid <= 1'b0;
            pend_seq   <= 3'd0;
            pend_uimm  <= 8'd0;
        end else if (halted) begin
            // freeze
        end else begin
            cycles <= cycles + 32'd1;
            if (mem_wait != 2'd0) begin
                mem_wait <= mem_wait - 2'd1;
                if (mem_wait == 2'd1) begin
                    mdr <= mem_rdata;
                    if (pend_valid) begin
                        pend_valid <= 1'b0;
                        apply_seq(pend_seq, pend_uimm);
                    end
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
                    if (dst == DST_MAR)
                        mar <= aluout;
                    if (we_ir)
                        ir <= mdr;
                    if (cw_re) begin
                        mem_wait   <= 2'd1;
                        pend_valid <= 1'b1;
                        pend_seq   <= seq;
                        pend_uimm  <= uimm;
                    end else if (seq == SEQ_DISPATCH) begin
                        // DISPATCH uses IR; we_ir may update IR this cycle — use mdr if we_ir
                        upc <= dispatch(we_ir ? mdr : ir);
                    end else
                        apply_seq(seq, uimm);
                end
            end
        end
    end
endmodule
