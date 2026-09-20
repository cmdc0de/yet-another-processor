// Icarus testbench: SRAM + yap_cpu.
// Plusargs: UCODE= SRAM= MAXCYCLES= ENTRY= P= IE= UBASE= ULIMIT= IRQ=
module tb;
    reg clk;
    reg rst;
    integer max_cycles;
    integer extra;
    integer i;
    integer fd;
    integer code;
    reg [31:0] entry;
    reg        init_p;
    reg        init_ie;
    reg [31:0] init_ubase;
    reg [31:0] init_ulimit;
    reg        irq_r;
    integer    p_i, ie_i, irq_i;
    reg [8*256-1:0] ucode_path;
    reg [8*256-1:0] sram_path;

    wire [31:0] mem_addr;
    wire        mem_re;
    wire        mem_we;
    wire [2:0]  mem_size;
    wire [31:0] mem_wdata;
    wire [31:0] mem_rdata;
    wire        halted;
    wire [31:0] pc;
    wire [31:0] ir;
    wire [31:0] cycles;
    wire [31:0] flags;
    wire [31:0] status;
    wire [31:0] cause_o;
    wire [31:0] epc;
    wire [31:0] ubase;
    wire [31:0] ulimit;
    wire [1023:0] gprs;

    reg [31:0] sram [0:16383];

    assign mem_rdata = sram[mem_addr[15:2]];

    yap_cpu dut (
        .clk(clk),
        .rst(rst),
        .irq(irq_r),
        .entry(entry),
        .init_p(init_p),
        .init_ie(init_ie),
        .init_ubase(init_ubase),
        .init_ulimit(init_ulimit),
        .mem_rdata(mem_rdata),
        .mem_addr(mem_addr),
        .mem_re(mem_re),
        .mem_we(mem_we),
        .mem_size(mem_size),
        .mem_wdata(mem_wdata),
        .halted(halted),
        .pc(pc),
        .ir(ir),
        .cycles(cycles),
        .flags(flags),
        .status(status),
        .cause_o(cause_o),
        .epc(epc),
        .ubase(ubase),
        .ulimit(ulimit),
        .gprs(gprs)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    always @(posedge clk) begin
        if (!rst && mem_we) begin
            if (mem_size == 3'd4)
                sram[mem_addr[15:2]] <= mem_wdata;
            else if (mem_size == 3'd2) begin
                if (mem_addr[1])
                    sram[mem_addr[15:2]][31:16] <= mem_wdata[15:0];
                else
                    sram[mem_addr[15:2]][15:0] <= mem_wdata[15:0];
            end else begin
                case (mem_addr[1:0])
                    2'd0: sram[mem_addr[15:2]][7:0]   <= mem_wdata[7:0];
                    2'd1: sram[mem_addr[15:2]][15:8]  <= mem_wdata[7:0];
                    2'd2: sram[mem_addr[15:2]][23:16] <= mem_wdata[7:0];
                    default: sram[mem_addr[15:2]][31:24] <= mem_wdata[7:0];
                endcase
            end
        end
    end

    initial begin
        entry = 32'd0;
        max_cycles = 100000;
        init_p = 1'b1;
        init_ie = 1'b0;
        init_ubase = 32'd0;
        init_ulimit = 32'h10000;
        irq_r = 1'b0;
        p_i = 1;
        ie_i = 0;
        irq_i = 0;
        if (!$value$plusargs("UCODE=%s", ucode_path)) begin
            $display("missing +UCODE=");
            $finish;
        end
        if (!$value$plusargs("SRAM=%s", sram_path)) begin
            $display("missing +SRAM=");
            $finish;
        end
        if ($value$plusargs("MAXCYCLES=%d", max_cycles)) begin
        end
        if ($value$plusargs("ENTRY=%h", entry)) begin
        end
        if ($value$plusargs("P=%d", p_i))
            init_p = (p_i != 0);
        if ($value$plusargs("IE=%d", ie_i))
            init_ie = (ie_i != 0);
        if ($value$plusargs("UBASE=%h", init_ubase)) begin
        end
        if ($value$plusargs("ULIMIT=%h", init_ulimit)) begin
        end
        if ($value$plusargs("IRQ=%d", irq_i))
            irq_r = (irq_i != 0);
        for (i = 0; i < 16384; i = i + 1)
            sram[i] = 32'd0;
        $readmemh(ucode_path, dut.ucode);
        $readmemh(sram_path, sram);
        rst = 1'b1;
        repeat (2) @(posedge clk);
        rst = 1'b0;
        extra = 0;
        begin : run
            forever begin
                @(posedge clk);
                if (halted) begin
                    extra = extra + 1;
                    if (extra == 3)
                        disable run;
                end else if (cycles >= max_cycles) begin
                    disable run;
                end
            end
        end
        $display("halted %0d", halted);
        $display("cycles %08x", cycles);
        $display("pc %08x", pc);
        $display("ir %08x", ir);
        $display("sram0 %08x", sram[0]);
        $display("sram12 %08x", sram[3]);
        $display("sram16 %08x", sram[4]);
        $display("sram20 %08x", sram[5]);
        $display("flags %08x", flags);
        $display("status %08x", status);
        $display("cause %08x", cause_o);
        $display("epc %08x", epc);
        $display("ubase %08x", ubase);
        $display("ulimit %08x", ulimit);
        for (i = 0; i < 32; i = i + 1)
            $display("r%0d %08x", i, gprs[32*i +: 32]);
        $finish;
    end
endmodule
