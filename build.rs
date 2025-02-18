fn main() {
    println!("cargo:rustc-link-search=native=ext/quicktree");
    println!("cargo:rustc-link-lib=static=quicktree");
}
