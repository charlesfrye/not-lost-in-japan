import modal

app = modal.App(name="omr-processor")

image = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-devel-ubuntu22.04", add_python="3.11")
    .apt_install("libgl1", "libglib2.0-0", "ghostscript", "git")
    .pip_install("oemer", "music21", "onnxruntime-gpu")
)

@app.function(
    image=image,
    gpu="A10G",
    timeout=600,
)
def process_image(image_bytes: bytes, filename: str) -> bytes:
    """Process a single image with oemer and return MIDI file bytes."""
    import subprocess
    from pathlib import Path
    from music21 import converter

    input_path = Path(f"/tmp/{filename}")
    with open(input_path, "wb") as f:
        f.write(image_bytes)

    output_dir = Path("/tmp/omr_output")
    output_dir.mkdir(exist_ok=True)

    result = subprocess.run(
        ["oemer", str(input_path), "-o", str(output_dir)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Oemer failed: {result.stderr}")

    musicxml_files = list(output_dir.glob("*.musicxml"))
    
    if not musicxml_files:
        raise RuntimeError(f"No MusicXML file generated. Files in output: {list(output_dir.iterdir())}")

    score = converter.parse(str(musicxml_files[0]))
    midi_path = output_dir / "output.midi"
    score.write("midi", fp=str(midi_path))

    with open(midi_path, "rb") as f:
        return f.read()

@app.local_entrypoint()
def main(image_path: str):
    """Process a PNG image and save MIDI file locally."""
    from pathlib import Path

    print(f"Processing {image_path}...")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    filename = Path(image_path).name
    midi_bytes = process_image.remote(image_bytes, filename)

    image_name = Path(image_path).stem
    output_filename = f"{image_name}.midi"
    with open(output_filename, "wb") as f:
        f.write(midi_bytes)

    print(f"Saved {output_filename}")
