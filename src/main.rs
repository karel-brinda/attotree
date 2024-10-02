use clap::{Parser, ArgAction};
use chrono::Local;
use std::fs::{File, OpenOptions};
use std::io::{self, BufRead, BufReader, Write, BufWriter};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::ffi::OsStr;
use tempfile::{Builder, TempDir};

#[derive(Parser, Debug)]
#[command(
    name = "attotree",
    version = "0.1.0",
    author = "Karel Brinda <karel.brinda@inria.fr>",
    about = "Rapid estimation of phylogenetic trees using sketching"
)]
struct Args {
    /// kmer size [21]
    #[arg(short = 'k', default_value_t = 21)]
    k: u32,

    /// sketch size [10000]
    #[arg(short = 's', default_value_t = 10000)]
    s: u32,

    /// number of threads [#cores]
    #[arg(short = 't')]
    t: Option<u32>,

    /// newick output [-]
    #[arg(short = 'o', default_value = "-")]
    o: String,

    /// tree construction method (nj/upgma) [nj]
    #[arg(short = 'm', default_value = "nj", value_parser = ["nj", "upgma"])]
    m: String,

    /// tmp dir [default system tmp dir]
    #[arg(short = 'd')]
    d: Option<String>,

    /// input files are list(s) of files
    #[arg(short = 'L', action = ArgAction::SetTrue)]
    L: bool,

    /// debugging (don't remove tmp dir)
    #[arg(short = 'D', action = ArgAction::SetTrue)]
    D: bool,

    /// verbose output
    #[arg(short = 'V', action = ArgAction::SetTrue)]
    V: bool,

    /// input genome file(s) (fasta / gzipped fasta / list of files when '-L')
    #[arg(required = true)]
    genome: Vec<String>,
}

fn main() {
    let args = Args::parse();

    let genomes: Vec<_> = args.genome.iter().map(|s| s.as_str()).collect();

    let k = args.k;
    let s = args.s;

    let t = args.t.unwrap_or_else(|| num_cpus::get() as u32);

    let o = &args.o;

    let m = &args.m;

    let d = args.d.as_deref();

    let L = args.L;

    let D = args.D;

    let V = args.V;

    attotree(
        &genomes,
        o,
        k,
        s,
        t,
        m,
        d,
        L,
        V,
        D,
    );
}

fn error(msg: &str) {
    eprintln!("attotree error: {}", msg);
    std::process::exit(1);
}

fn message(msg: &str) {
    let dt = Local::now();
    let fdt = dt.format("%Y-%m-%d %H:%M:%S").to_string();
    eprintln!("[attotree] {} {}", fdt, msg);
}

fn shorten_output(s: &str) -> String {
    if s.len() > 40 {
        format!("{}...", &s[..40])
    } else {
        s.to_string()
    }
}

fn run_safe(
    command: &[&str],
    output_fn: Option<&Path>,
    verbose: bool,
    silent: bool,
    err_msg: Option<&str>,
    thr_exc: bool,
) {
    let command_str = command.join(" ");
    let command_str_nice = if verbose {
        command_str.clone()
    } else {
        shorten_output(&command_str)
    };

    if !silent {
        message(&format!("Shell command: '{}'", command_str_nice));
    }

    let mut cmd = Command::new("/bin/bash");
    cmd.arg("-e")
        .arg("-o")
        .arg("pipefail")
        .arg("-c")
        .arg(&command_str);

    if let Some(output_fn) = output_fn {
        let output_file = File::create(output_fn).expect("Failed to open output file");
        cmd.stdout(Stdio::from(output_file));
    } else {
        cmd.stdout(Stdio::inherit());
    }

    let status = cmd.status().expect("Failed to execute command");

    if status.success() {
        if !silent {
            message(&format!("Finished: '{}'", command_str_nice));
        }
    } else {
        message(&format!(
            "Unfinished, an error occurred (error code {:?}): '{}'",
            status.code(),
            command_str
        ));
        if let Some(err_msg) = err_msg {
            eprintln!("Error: {}", err_msg);
        }
        if thr_exc {
            error("A command failed, see messages above.");
        }
        std::process::exit(1);
    }
}

fn mash_triangle(
    inp_fns: &[&str],
    phylip_fn: &Path,
    k: u32,
    s: u32,
    t: u32,
    fof: bool,
    verbose: bool,
) {
    message("Running Mash");
    let mut cmd: Vec<String> = vec![
        "mash".to_string(),
        "triangle".to_string(),
        "-s".to_string(),
        s.to_string(),
        "-k".to_string(),
        k.to_string(),
        "-p".to_string(),
        t.to_string(),
    ];
    if fof {
        cmd.push("-l".to_string());
    }
    cmd.extend(inp_fns.iter().map(|s| s.to_string()));
    let cmd_str = cmd.join(" ");
    run_safe(
        &[&cmd_str],
        Some(phylip_fn),
        verbose,
        false,
        None,
        true,
    );
}

fn fn_to_node_name(filename: &str) -> String {
    let basename = Path::new(filename)
        .file_name()
        .unwrap_or_else(|| OsStr::new(""))
        .to_str()
        .unwrap_or("");
    let mut basename_components: Vec<&str> = basename.split('.').collect();
    if basename_components.len() == 1 {
        basename_components.push("");
    }
    basename_components.pop();
    let nname = basename_components.join(".");
    nname
}

fn postprocess_mash_phylip(phylip_in_fn: &Path, phylip_out_fn: &Path, _verbose: bool) {
    let f = File::open(phylip_in_fn).expect("Failed to open phylip input file");
    let reader = BufReader::new(f);
    let g = File::create(phylip_out_fn).expect("Failed to create phylip output file");
    let mut writer = BufWriter::new(g);
    for (i, line) in reader.lines().enumerate() {
        let mut x = line.expect("Failed to read line").trim().to_string();
        if i != 0 {
            let mut parts = x.splitn(2, '\t');
            let l = parts.next().unwrap_or("");
            let r = parts.next().unwrap_or("");
            let l = fn_to_node_name(l);
            x = format!("{}\t{}", l, r);
        }
        writeln!(writer, "{}", x).expect("Failed to write line");
    }
}

fn quicktree(phylip_fn: &Path, newick_fn: &Path, algorithm: &str, verbose: bool) {
    message("Running Quicktree");
    let mut cmd: Vec<String> = vec![
        "quicktree".to_string(),
        "-in".to_string(),
        "m".to_string(),
    ];
    if algorithm == "upgma" {
        cmd.push("-upgma".to_string());
    }
    cmd.push(phylip_fn.to_str().unwrap().to_string());
    let cmd_str = cmd.join(" ");
    run_safe(
        &[&cmd_str],
        Some(newick_fn),
        verbose,
        false,
        None,
        true,
    );
}

fn postprocess_quicktree_nw(nw_in_fn: &Path, nw_out_fn: &Path, _verbose: bool) {
    message("Postprocessing tree");
    let f = File::open(nw_in_fn).expect("Failed to open newick input file");
    let reader = BufReader::new(f);
    let mut buffer = String::new();
    for line in reader.lines() {
        let x = line.expect("Failed to read line").trim().to_string();
        buffer.push_str(&x);
    }
    if nw_out_fn.to_str().unwrap() == "-" {
        println!("{}", buffer);
    } else {
        let mut fo = File::create(nw_out_fn).expect("Failed to create newick output file");
        fo.write_all(buffer.as_bytes())
            .expect("Failed to write newick output");
    }
}

fn attotree(
    fns: &[&str],
    newick_fn: &str,
    k: u32,
    s: u32,
    t: u32,
    phylogeny_algorithm: &str,
    tmp_dir: Option<&str>,
    fof: bool,
    verbose: bool,
    debug: bool,
) {
    let mut features = Vec::new();
    if verbose {
        features.push("verbose");
    }
    if debug {
        features.push("debugging");
    }
    let fmsg = if !features.is_empty() {
        format!(" ({})", features.join(", "))
    } else {
        String::new()
    };
    message(&format!("Attotree starting{}", fmsg));

    let temp_dir = if let Some(tmp_dir) = tmp_dir {
        Builder::new()
            .prefix("attotree")
            .tempdir_in(tmp_dir)
            .expect("Failed to create temp dir")
    } else {
        Builder::new()
            .prefix("attotree")
            .tempdir()
            .expect("Failed to create temp dir")
    };
    let d = temp_dir.path();
    message(&format!("Creating a temporary directory {:?}", d));

    let phylip1_fn = d.join("distances.phylip0");
    let phylip2_fn = d.join("distances.phylip");
    let newick1_fn = d.join("tree.nw");
    let newick2_fn = PathBuf::from(newick_fn);

    let fns = if fof {
        // This is to make the list of files passed to Mash even with
        // process substitutions and allows for merging multiple lists
        let new_fof_fn = d.join("fof.txt");
        {
            let mut g = File::create(&new_fof_fn).expect("Failed to create new fof file");
            for old_fof_fn in fns {
                let f = File::open(old_fof_fn).expect("Failed to open old fof file");
                let reader = BufReader::new(f);
                for line in reader.lines() {
                    let line = line.expect("Failed to read line");
                    writeln!(g, "{}", line.trim()).expect("Failed to write to new fof file");
                }
            }
        }
        vec![new_fof_fn.to_str().unwrap()]
    } else {
        fns.to_vec()
    };

    mash_triangle(&fns, &phylip1_fn, k, s, t, fof, verbose);
    postprocess_mash_phylip(&phylip1_fn, &phylip2_fn, verbose);
    quicktree(&phylip2_fn, &newick1_fn, phylogeny_algorithm, verbose);
    postprocess_quicktree_nw(&newick1_fn, &newick2_fn, verbose);

    let emsg = if debug {
        let temp_dir_path = temp_dir.into_path();
        format!(" (auxiliary files retained in '{:?}')", temp_dir_path)
    } else {
        message(&format!(
            "Deleting the temporary directory {:?}",
            d
        ));
        // TempDir is dropped here, and the directory is deleted
        String::new()
    };
    message(&format!("Attotree finished{}", emsg));
}
