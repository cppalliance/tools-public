use std::env;
use std::fs;
use std::io::BufWriter;
use std::path::Path;

use anyhow::{bail, Context};
use image::codecs::jpeg::JpegEncoder;
use image::imageops::FilterType;
use image::{DynamicImage, GenericImageView, ImageBuffer, ImageReader, Rgb, RgbImage};

const JPEG_QUALITY: u8 = 50;
const MAX_WIDTH: u32 = 1024;

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

/// Flatten any alpha channel onto white, so transparent regions do not turn black in JPEG.
fn flatten_on_white(img: &DynamicImage) -> RgbImage {
    if !img.color().has_alpha() {
        return img.to_rgb8();
    }
    let rgba = img.to_rgba8();
    let (w, h) = rgba.dimensions();
    ImageBuffer::from_fn(w, h, |x, y| {
        let p = rgba.get_pixel(x, y).0;
        let a = u32::from(p[3]);
        let blend = |c: u8| -> u8 {
            let v = (u32::from(c) * a + 255 * (255 - a)) / 255;
            u8::try_from(v).unwrap_or(255)
        };
        Rgb([blend(p[0]), blend(p[1]), blend(p[2])])
    })
}

/// Rewrite `images/<stem>.png` to `images/<stem>.jpg` in every `.md` beside the `images/` directory.
/// Preserves bytes otherwise, including line endings.
fn rewrite_markdown(png_path: &Path) -> anyhow::Result<()> {
    let Some(images_dir) = png_path.parent() else {
        return Ok(());
    };
    if images_dir.file_name().and_then(|n| n.to_str()) != Some("images") {
        return Ok(());
    }
    let Some(group_dir) = images_dir.parent() else {
        return Ok(());
    };
    let group_dir = if group_dir.as_os_str().is_empty() {
        Path::new(".")
    } else {
        group_dir
    };
    let Some(stem) = png_path.file_stem().and_then(|s| s.to_str()) else {
        return Ok(());
    };
    let from = format!("images/{stem}.png");
    let to = format!("images/{stem}.jpg");

    for entry in fs::read_dir(group_dir).with_context(|| format!("read {}", group_dir.display()))? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) != Some("md") {
            continue;
        }
        let text = fs::read_to_string(&path).with_context(|| format!("read {}", path.display()))?;
        if !text.contains(&from) {
            continue;
        }
        let updated = text.replace(&from, &to);
        fs::write(&path, updated).with_context(|| format!("write {}", path.display()))?;
        println!("  rewrote {} ({} -> {})", path.display(), from, to);
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

    // Decode by content, not extension: some files carry a `.png` name over JPEG bytes.
    let img = ImageReader::open(png_path)
        .with_context(|| format!("open {}", png_path.display()))?
        .with_guessed_format()
        .with_context(|| format!("sniff {}", png_path.display()))?
        .decode()
        .with_context(|| format!("decode {}", png_path.display()))?;
    let (orig_w, orig_h) = img.dimensions();
    let img = if orig_w > MAX_WIDTH {
        img.resize(MAX_WIDTH, u32::MAX, FilterType::Lanczos3)
    } else {
        img
    };
    let (w, h) = img.dimensions();
    let rgb = flatten_on_white(&img);

    let jpg_path = png_path.with_extension("jpg");
    let file = fs::File::create(&jpg_path)
        .with_context(|| format!("create {}", jpg_path.display()))?;
    let mut writer = BufWriter::new(file);
    let encoder = JpegEncoder::new_with_quality(&mut writer, JPEG_QUALITY);
    rgb.write_with_encoder(encoder)
        .with_context(|| format!("encode {}", jpg_path.display()))?;
    drop(writer);

    let jpg_size = fs::metadata(&jpg_path)
        .with_context(|| format!("stat {}", jpg_path.display()))?
        .len();

    println!(
        "{} -> {} ({orig_w}x{orig_h} -> {w}x{h}, {} KB -> {} KB)",
        png_path.display(),
        jpg_path.display(),
        png_size / 1024,
        jpg_size / 1024,
    );

    rewrite_markdown(png_path)
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
