//! yap-compiler: `.ys` → YAP1 (load=0, entry=0).
//! Layout: j _start @0, halt @0x80, _start @0x84 (li sp, jal main, halt), then fns.

use std::env;
use std::fs;
use std::path::Path;
use std::process;

const OPCODE_J: u32 = 0b000010;
const OPCODE_JAL: u32 = 0b000011;
const OPCODE_ADDI: u32 = 0b001000;
const OPCODE_ORI: u32 = 0b001101;
const OPCODE_LUI: u32 = 0b001111;
const OPCODE_LW: u32 = 0b100011;
const OPCODE_SW: u32 = 0b101011;
const FUNCT_JR: u32 = 0b001000;
const FUNCT_ADD: u32 = 0b100000;
const FUNCT_SUB: u32 = 0b100010;
const FUNCT_HALT: u32 = 0b101100;
const ZERO: u32 = 0;
const RA: u32 = 3;
const SP: u32 = 4;
const A0: u32 = 5;
const T0: u32 = 10;
const ADDR_START: u32 = 0x84;
const ADDR_CODE: u32 = 0x94;

fn pack_r(rd: u32, rs: u32, rt: u32, shamt: u32, funct: u32) -> u32 {
    (rd << 21) | (rs << 16) | (rt << 11) | (shamt << 6) | funct
}

fn pack_i(opcode: u32, rd: u32, rs: u32, imm16: u32) -> u32 {
    (opcode << 26) | (rd << 21) | (rs << 16) | (imm16 & 0xffff)
}

fn pack_j(opcode: u32, addr: u32) -> u32 {
    (opcode << 26) | ((addr >> 2) & 0x03ff_ffff)
}

fn halt() -> u32 {
    pack_r(0, 0, 0, 0, FUNCT_HALT)
}

fn jr_ra() -> u32 {
    pack_r(0, RA, 0, 0, FUNCT_JR)
}

fn addi(rd: u32, rs: u32, imm: i32) -> u32 {
    pack_i(OPCODE_ADDI, rd, rs, imm as u32)
}

fn li(rd: u32, imm: i32) -> Vec<u32> {
    if (-0x8000..=0x7fff).contains(&imm) {
        vec![addi(rd, ZERO, imm)]
    } else {
        let u = imm as u32;
        vec![
            pack_i(OPCODE_LUI, rd, 0, u >> 16),
            pack_i(OPCODE_ORI, rd, rd, u),
        ]
    }
}

#[derive(Clone, Debug)]
enum Tok {
    Fn,
    Return,
    Ident(String),
    Int(i32),
    LParen,
    RParen,
    LBrace,
    RBrace,
    Comma,
    Semi,
    Plus,
    Minus,
    Eq,
    Eof,
}

struct Lexer<'a> {
    src: &'a str,
    pos: usize,
    line: usize,
}

impl<'a> Lexer<'a> {
    fn new(src: &'a str) -> Self {
        Self { src, pos: 0, line: 1 }
    }

    fn peek_char(&self) -> Option<char> {
        self.src[self.pos..].chars().next()
    }

    fn bump(&mut self) -> Option<char> {
        let c = self.peek_char()?;
        self.pos += c.len_utf8();
        if c == '\n' {
            self.line += 1;
        }
        Some(c)
    }

    fn skip_ws_comments(&mut self) {
        loop {
            while matches!(self.peek_char(), Some(c) if c.is_whitespace()) {
                self.bump();
            }
            if self.src[self.pos..].starts_with("//") {
                while matches!(self.peek_char(), Some(c) if c != '\n') {
                    self.bump();
                }
                continue;
            }
            break;
        }
    }

    fn next_tok(&mut self) -> Result<(Tok, usize), String> {
        self.skip_ws_comments();
        let line = self.line;
        let Some(c) = self.peek_char() else {
            return Ok((Tok::Eof, line));
        };
        match c {
            '(' => {
                self.bump();
                Ok((Tok::LParen, line))
            }
            ')' => {
                self.bump();
                Ok((Tok::RParen, line))
            }
            '{' => {
                self.bump();
                Ok((Tok::LBrace, line))
            }
            '}' => {
                self.bump();
                Ok((Tok::RBrace, line))
            }
            ',' => {
                self.bump();
                Ok((Tok::Comma, line))
            }
            ';' => {
                self.bump();
                Ok((Tok::Semi, line))
            }
            '+' => {
                self.bump();
                Ok((Tok::Plus, line))
            }
            '-' => {
                self.bump();
                Ok((Tok::Minus, line))
            }
            '=' => {
                self.bump();
                Ok((Tok::Eq, line))
            }
            '0'..='9' => {
                let start = self.pos;
                if self.src[self.pos..].starts_with("0x") || self.src[self.pos..].starts_with("0X") {
                    self.bump();
                    self.bump();
                    while matches!(self.peek_char(), Some(c) if c.is_ascii_hexdigit()) {
                        self.bump();
                    }
                } else {
                    while matches!(self.peek_char(), Some(c) if c.is_ascii_digit()) {
                        self.bump();
                    }
                }
                let s = &self.src[start..self.pos];
                let v = i32::from_str_radix(
                    s.trim_start_matches("0x").trim_start_matches("0X"),
                    if s.starts_with("0x") || s.starts_with("0X") { 16 } else { 10 },
                )
                .map_err(|_| format!(":{}: bad integer {s}", line))?;
                Ok((Tok::Int(v), line))
            }
            'A'..='Z' | 'a'..='z' | '_' => {
                let start = self.pos;
                self.bump();
                while matches!(self.peek_char(), Some(c) if c.is_ascii_alphanumeric() || c == '_') {
                    self.bump();
                }
                let s = &self.src[start..self.pos];
                let tok = match s {
                    "fn" => Tok::Fn,
                    "return" => Tok::Return,
                    _ => Tok::Ident(s.to_string()),
                };
                Ok((tok, line))
            }
            _ => Err(format!(":{}: unexpected character {c:?}", line)),
        }
    }
}

#[derive(Clone)]
enum Expr {
    Int(i32),
    Var(String),
    Call(String, Vec<Expr>),
    Add(Box<Expr>, Box<Expr>),
    Sub(Box<Expr>, Box<Expr>),
}

enum Stmt {
    Return(Expr),
    Assign(String, Expr),
    Expr(Expr),
}

struct FnDef {
    name: String,
    params: Vec<String>,
    body: Vec<Stmt>,
}

struct Parser {
    toks: Vec<(Tok, usize)>,
    i: usize,
    path: String,
}

impl Parser {
    fn peek(&self) -> &Tok {
        self.toks.get(self.i).map(|(t, _)| t).unwrap_or(&Tok::Eof)
    }

    fn line(&self) -> usize {
        self.toks.get(self.i).map(|(_, l)| *l).unwrap_or(1)
    }

    fn bump(&mut self) -> Tok {
        let t = self.peek().clone();
        if self.i < self.toks.len() {
            self.i += 1;
        }
        t
    }

    fn err(&self, msg: &str) -> String {
        format!("{}:{}: {msg}", self.path, self.line())
    }

    fn expect(&mut self, want: &str, ok: impl Fn(&Tok) -> bool) -> Result<Tok, String> {
        if ok(self.peek()) {
            Ok(self.bump())
        } else {
            Err(self.err(&format!("expected {want}")))
        }
    }

    fn parse_program(&mut self) -> Result<Vec<FnDef>, String> {
        let mut fns = Vec::new();
        while !matches!(self.peek(), Tok::Eof) {
            fns.push(self.parse_fn()?);
        }
        if !fns.iter().any(|f| f.name == "main") {
            return Err(format!("{}:1: missing fn main", self.path));
        }
        Ok(fns)
    }

    fn parse_fn(&mut self) -> Result<FnDef, String> {
        self.expect("fn", |t| matches!(t, Tok::Fn))?;
        let Tok::Ident(name) = self.expect("name", |t| matches!(t, Tok::Ident(_)))? else {
            unreachable!()
        };
        self.expect("(", |t| matches!(t, Tok::LParen))?;
        let mut params = Vec::new();
        if !matches!(self.peek(), Tok::RParen) {
            loop {
                let Tok::Ident(p) = self.expect("param", |t| matches!(t, Tok::Ident(_)))? else {
                    unreachable!()
                };
                params.push(p);
                if matches!(self.peek(), Tok::Comma) {
                    self.bump();
                    continue;
                }
                break;
            }
        }
        if params.len() > 4 {
            return Err(self.err("at most 4 parameters"));
        }
        if name == "main" && !params.is_empty() {
            return Err(self.err("main takes no parameters"));
        }
        self.expect(")", |t| matches!(t, Tok::RParen))?;
        self.expect("{", |t| matches!(t, Tok::LBrace))?;
        let mut body = Vec::new();
        while !matches!(self.peek(), Tok::RBrace) {
            if matches!(self.peek(), Tok::Eof) {
                return Err(self.err("unclosed function"));
            }
            body.push(self.parse_stmt()?);
        }
        self.bump();
        Ok(FnDef { name, params, body })
    }

    fn parse_stmt(&mut self) -> Result<Stmt, String> {
        if matches!(self.peek(), Tok::Return) {
            self.bump();
            let e = self.parse_expr()?;
            self.expect(";", |t| matches!(t, Tok::Semi))?;
            return Ok(Stmt::Return(e));
        }
        if let Tok::Ident(name) = self.peek().clone() {
            let save = self.i;
            self.bump();
            if matches!(self.peek(), Tok::Eq) {
                self.bump();
                let e = self.parse_expr()?;
                self.expect(";", |t| matches!(t, Tok::Semi))?;
                return Ok(Stmt::Assign(name, e));
            }
            self.i = save;
        }
        let e = self.parse_expr()?;
        self.expect(";", |t| matches!(t, Tok::Semi))?;
        Ok(Stmt::Expr(e))
    }

    fn parse_expr(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_term()?;
        loop {
            match self.peek() {
                Tok::Plus => {
                    self.bump();
                    let right = self.parse_term()?;
                    left = Expr::Add(Box::new(left), Box::new(right));
                }
                Tok::Minus => {
                    self.bump();
                    let right = self.parse_term()?;
                    left = Expr::Sub(Box::new(left), Box::new(right));
                }
                _ => break,
            }
        }
        Ok(left)
    }

    fn parse_term(&mut self) -> Result<Expr, String> {
        match self.peek().clone() {
            Tok::Minus => {
                self.bump();
                match self.bump() {
                    Tok::Int(v) => Ok(Expr::Int(v.wrapping_neg())),
                    _ => Err(self.err("expected integer after -")),
                }
            }
            Tok::Int(v) => {
                self.bump();
                Ok(Expr::Int(v))
            }
            Tok::Ident(name) => {
                self.bump();
                if matches!(self.peek(), Tok::LParen) {
                    self.bump();
                    let mut args = Vec::new();
                    if !matches!(self.peek(), Tok::RParen) {
                        loop {
                            args.push(self.parse_expr()?);
                            if matches!(self.peek(), Tok::Comma) {
                                self.bump();
                                continue;
                            }
                            break;
                        }
                    }
                    if args.len() > 4 {
                        return Err(self.err("at most 4 arguments"));
                    }
                    self.expect(")", |t| matches!(t, Tok::RParen))?;
                    Ok(Expr::Call(name, args))
                } else {
                    Ok(Expr::Var(name))
                }
            }
            Tok::LParen => {
                self.bump();
                let e = self.parse_expr()?;
                self.expect(")", |t| matches!(t, Tok::RParen))?;
                Ok(e)
            }
            _ => Err(self.err("expected expression")),
        }
    }
}

fn tokenize(src: &str, path: &str) -> Result<Vec<(Tok, usize)>, String> {
    let mut lx = Lexer::new(src);
    let mut out = Vec::new();
    loop {
        let (t, line) = lx.next_tok().map_err(|e| format!("{path}{e}"))?;
        let eof = matches!(t, Tok::Eof);
        out.push((t, line));
        if eof {
            break;
        }
    }
    Ok(out)
}

fn env_reg(name: &str, params: &[String]) -> Option<u32> {
    params.iter().position(|p| p == name).map(|i| A0 + i as u32)
}

#[derive(Clone)]
enum Word {
    Raw(u32),
    Jal(String),
}

fn emit_expr_w(
    e: &Expr,
    dest: u32,
    params: &[String],
    out: &mut Vec<Word>,
    tmp: &mut u32,
) -> Result<(), String> {
    match e {
        Expr::Int(v) => {
            for w in li(dest, *v) {
                out.push(Word::Raw(w));
            }
        }
        Expr::Var(name) => {
            let r = env_reg(name, params).ok_or_else(|| format!("unknown name {name}"))?;
            if r != dest {
                out.push(Word::Raw(pack_r(dest, r, ZERO, 0, FUNCT_ADD)));
            }
        }
        Expr::Add(a, b) | Expr::Sub(a, b) => {
            let t1 = *tmp;
            *tmp += 1;
            let t2 = *tmp;
            *tmp += 1;
            emit_expr_w(a, t1, params, out, tmp)?;
            emit_expr_w(b, t2, params, out, tmp)?;
            let funct = if matches!(e, Expr::Add(_, _)) {
                FUNCT_ADD
            } else {
                FUNCT_SUB
            };
            out.push(Word::Raw(pack_r(dest, t1, t2, 0, funct)));
        }
        Expr::Call(name, args) => {
            for (i, arg) in args.iter().enumerate() {
                let mut t = T0 + 2;
                emit_expr_w(arg, A0 + i as u32, params, out, &mut t)?;
            }
            out.push(Word::Jal(name.clone()));
            if dest != A0 {
                out.push(Word::Raw(pack_r(dest, A0, ZERO, 0, FUNCT_ADD)));
            }
        }
    }
    Ok(())
}

fn fn_makes_call(body: &[Stmt]) -> bool {
    fn expr_calls(e: &Expr) -> bool {
        match e {
            Expr::Call(_, _) => true,
            Expr::Add(a, b) | Expr::Sub(a, b) => expr_calls(a) || expr_calls(b),
            _ => false,
        }
    }
    body.iter().any(|s| match s {
        Stmt::Return(e) | Stmt::Assign(_, e) | Stmt::Expr(e) => expr_calls(e),
    })
}

fn compile_fn(f: &FnDef) -> Result<Vec<Word>, String> {
    let mut out = Vec::new();
    let calls = fn_makes_call(&f.body);
    if calls {
        out.push(Word::Raw(addi(SP, SP, -8)));
        out.push(Word::Raw(pack_i(OPCODE_SW, RA, SP, 4)));
    }
    let mut saw_return = false;
    for stmt in &f.body {
        let mut tmp = T0;
        match stmt {
            Stmt::Return(e) => {
                emit_expr_w(e, A0, &f.params, &mut out, &mut tmp)?;
                saw_return = true;
                break;
            }
            Stmt::Assign(_, e) | Stmt::Expr(e) => {
                emit_expr_w(e, A0, &f.params, &mut out, &mut tmp)?;
            }
        }
    }
    let _ = saw_return;
    if calls {
        out.push(Word::Raw(pack_i(OPCODE_LW, RA, SP, 4)));
        out.push(Word::Raw(addi(SP, SP, 8)));
    }
    out.push(Word::Raw(jr_ra()));
    Ok(out)
}

fn compile_program(fns: &[FnDef]) -> Result<Vec<u8>, String> {
    let mut compiled: Vec<(String, Vec<Word>)> = Vec::new();
    for f in fns {
        compiled.push((f.name.clone(), compile_fn(f)?));
    }
    let mut addr = ADDR_CODE;
    let mut addrs = std::collections::HashMap::new();
    for (name, words) in &compiled {
        addrs.insert(name.clone(), addr);
        addr += 4 * words.len() as u32;
    }
    let main_addr = *addrs.get("main").ok_or("missing main")?;
    let mut payload = vec![0u8; addr as usize];
    let mut put = |a: u32, w: u32| {
        let i = a as usize;
        payload[i..i + 4].copy_from_slice(&w.to_le_bytes());
    };
    put(0, pack_j(OPCODE_J, ADDR_START));
    put(0x80, halt());
    put(0x84, pack_i(OPCODE_LUI, SP, 0, 0));
    put(0x88, pack_i(OPCODE_ORI, SP, SP, 0x8000));
    put(0x8c, pack_j(OPCODE_JAL, main_addr));
    put(0x90, halt());
    for (name, words) in &compiled {
        let mut a = addrs[name];
        for w in words {
            let word = match w {
                Word::Raw(x) => *x,
                Word::Jal(n) => {
                    let t = *addrs.get(n).ok_or_else(|| format!("unknown function {n}"))?;
                    pack_j(OPCODE_JAL, t)
                }
            };
            put(a, word);
            a += 4;
        }
    }
    Ok(payload)
}

fn pack_yap1(payload: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(16 + payload.len());
    out.extend_from_slice(b"YAP1");
    out.extend_from_slice(&0u32.to_le_bytes());
    out.extend_from_slice(&(payload.len() as u32).to_le_bytes());
    out.extend_from_slice(&0u32.to_le_bytes());
    out.extend_from_slice(payload);
    out
}

fn compile_file(input: &Path, output: &Path) -> Result<(), String> {
    let path = input.display().to_string();
    let src = fs::read_to_string(input).map_err(|e| format!("{path}:1: {e}"))?;
    let toks = tokenize(&src, &path)?;
    let mut p = Parser {
        toks,
        i: 0,
        path: path.clone(),
    };
    let fns = p.parse_program()?;
    let payload = compile_program(&fns).map_err(|e| format!("{path}:1: {e}"))?;
    let image = pack_yap1(&payload);
    fs::write(output, image).map_err(|e| format!("{}:1: {e}", output.display()))?;
    Ok(())
}

fn usage() -> ! {
    eprintln!("usage: yap-compiler input.ys -o output.yap");
    process::exit(2);
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let mut input: Option<String> = None;
    let mut output: Option<String> = None;
    let mut i = 0;
    while i < args.len() {
        if args[i] == "-o" {
            i += 1;
            if i >= args.len() {
                usage();
            }
            output = Some(args[i].clone());
        } else if args[i].starts_with('-') {
            usage();
        } else if input.is_none() {
            input = Some(args[i].clone());
        } else {
            usage();
        }
        i += 1;
    }
    let (Some(input), Some(output)) = (input, output) else {
        usage();
    };
    if let Err(e) = compile_file(Path::new(&input), Path::new(&output)) {
        eprintln!("{e}");
        process::exit(1);
    }
}
