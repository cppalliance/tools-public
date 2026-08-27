use std::env;
use std::fs;
use std::io::BufWriter;
use std::path::Path;

use anyhow::{bail, Context};
use image::codecs::jpeg::JpegEncoder;

const JPEG_QUALITY: u8 = 50;

fn run() -> anyhow::Result<()> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() {
        bail!("usage: png2jpg <file.png> [file2.png ...]");
    }

    for arg in &args {
        convert(Path::new(arg))?;
    }
    Ok(())
}

fn convert(png_path: &Path) -> anyhow::Result<()> {
    let ext = png_path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("");
    if !ext.eq_ignore_ascii_case("png") {
        bail!("{}: not a .png file", png_path.display());
    }
    if !png_path.exists() {
        bail!("{}: file not found", png_path.display());
    }

    let png_size = fs::metadata(png_path)
        .with_context(|| format!("stat {}", png_path.display()))?
        .len();

    let img = image::open(png_path)
        .with_context(|| format!("open {}", png_path.display()))?
        .to_rgb8();

    let jpg_path = png_path.with_extension("jpg");
    let file = fs::File::create(&jpg_path)
        .with_context(|| format!("create {}", jpg_path.display()))?;
    let mut writer = BufWriter::new(file);
    let encoder = JpegEncoder::new_with_quality(&mut writer, JPEG_QUALITY);
    img.write_with_encoder(encoder)
        .with_context(|| format!("encode {}", jpg_path.display()))?;
    drop(writer);

    let jpg_size = fs::metadata(&jpg_path)
        .with_context(|| format!("stat {}", jpg_path.display()))?
        .len();

    println!(
        "{} -> {} ({} KB -> {} KB)",
        png_path.display(),
        jpg_path.display(),
        png_size / 1024,
        jpg_size / 1024,
    );
    Ok(())
}

fn main() -> std::process::ExitCode {
    match run() {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("png2jpg: {e:?}");
            std::process::ExitCode::from(2)
        }
    }
}
