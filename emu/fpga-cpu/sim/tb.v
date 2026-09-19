// Icarus testbench: SRAM + yap_cpu. Plusargs: UCODE= SRAM= MAXCYCLES= ENTRY=
module tb;
    reg clk;
    reg rst;
    integer max_cycles;
    integer extra;
    integer i;
    integer fd;
    integer code;
    reg [31:0] entry;
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

    reg [31:0] sram [0:16383];

    assign mem_rdata = sram[mem_addr[15:2]];

    yap_cpu dut (
        .clk(clk),
        .rst(rst),
        .irq(1'b0),
        .entry(entry),
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
        .ulimit(ulimit)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        entry = 32'd0;
        max_cycles = 100000;
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
        $display("flags %08x", flags);
        $display("status %08x", status);
        $display("cause %08x", cause_o);
        $display("epc %08x", epc);
        $display("ubase %08x", ubase);
        $display("ulimit %08x", ulimit);
        $display("r0 00000000");
        $display("r1 00000001");
        $display("r2 ffffffff");
        for (i = 3; i < 32; i = i + 1)
            $display("r%0d 00000000", i);
        $finish;
    end
endmodule
