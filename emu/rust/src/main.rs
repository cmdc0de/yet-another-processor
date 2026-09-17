fn main() {
    std::process::exit(yap_emu::cli(std::env::args().skip(1)));
}
