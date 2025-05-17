from dji_thermal_sdk.dji_sdk import dji_init
from dji_thermal_sdk.utility import rjpeg_to_heatmap
import numpy as np
from pathlib import Path
from PIL import Image
import datetime
import tifffile
import piexif

ROOT = Path(__file__).resolve().parent


def load_thermal_array(rjpeg_path: str) -> np.ndarray:
    """
    Decode an R-JPEG into a NumPy array of floating-point temperatures (°C).

    Parameters
    ----------
    rjpeg_path : str
        Path to the radiometric JPEG produced by the Matrice 3TD.

    Returns
    -------
    temps : np.ndarray of shape (H, W), dtype float32
        Per-pixel temperatures in degrees Celsius.
    """
    # 1) Initialize the DJI SDK once
    sdk_path = ROOT / "venv/tsdk/utility/bin/linux/release_x64/libdirp.so"
    dji_init(str(sdk_path))

    # 2) Decode directly to a float32 °C array
    temps = rjpeg_to_heatmap(str(Path(rjpeg_path)), dtype="float32")
    return temps


def save_thermal_jpeg_with_exif(src_rjpeg: str, temps: np.ndarray) -> Path:
    """
    Create an 8-bit thermal JPEG from `temps`, preserving EXIF from `src_rjpeg`.

    - Scales `temps` linearly from its own min/max → 0–255.
    - Reads EXIF from `src_rjpeg` (incl. GPS, timestamp, etc).
    - Embeds that EXIF into the new JPEG.
    - Writes to results/thermal_YYYYMMDD_HHMMSS.jpg.

    Returns the Path to the saved file.
    """
    src = Path(src_rjpeg)
    if not src.is_file():
        raise FileNotFoundError(f"Source JPEG not found: {src}")

    # 1) Extract EXIF bytes from source
    exif_dict = piexif.load(str(src))
    exif_bytes = piexif.dump(exif_dict)

    # 2) Normalize temps → 0–255
    vmin, vmax = float(np.nanmin(temps)), float(np.nanmax(temps))
    if vmax == vmin:
        raise ValueError("Temperature array is constant.")
    norm = np.clip((temps - vmin) / (vmax - vmin), 0.0, 1.0)
    img8 = np.rint(norm * 255).astype(np.uint8)

    # 3) Build output filename & ensure folder exists
    out_folder = ROOT / "results"
    out_folder.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_folder / f"thermal_{stamp}.jpg"

    # 4) Save provisional JPEG without EXIF
    pil = Image.fromarray(img8, mode="L")
    pil.save(str(out_path), format="JPEG", quality=90)

    # 5) Insert original EXIF into it
    piexif.insert(exif_bytes, str(out_path))
    return out_path


def save_thermal_tiff(temps, out_dir="results"):
    """
    Save a float32 temperature array as a single-band GeoTIFF.
    """
    out_dir = Path(ROOT / out_dir)
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "thermal_float32.tif"
    tifffile.imwrite(str(path), temps, dtype="float32")
    return path


def save_thermal_png16(temps, out_dir="results", scale=100):
    """
    Scale float32 temps (°C) by `scale` and save as 16-bit PNG.
    """
    arr16 = np.round(temps * scale).astype(np.uint16)
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "thermal_16bit.png"
    Image.fromarray(arr16, mode="I;16").save(path)
    return path


if __name__ == "__main__":
    # 1) Define source radiometric JPEG
    src_jpeg = ROOT / "venv/tsdk/dataset/M3TD/DJI_0003_R.JPG"

    # 2) Decode temperature array
    arr = load_thermal_array(str(src_jpeg))
    print("Array shape:", arr.shape)
    print(f"Min temp = {arr.min():.1f} °C, Max temp = {arr.max():.1f} °C")

    # 3) Save thermal JPEG with original EXIF
    jpg_path = save_thermal_jpeg_with_exif(str(src_jpeg), arr)
    print("Wrote JPEG with EXIF preserved:", jpg_path)

    # 4) Save float TIFF and 16-bit PNG
    tiff_path = save_thermal_tiff(arr)
    print("Wrote float TIFF:", tiff_path)
    png16_path = save_thermal_png16(arr)
    print("Wrote 16-bit PNG:", png16_path)
