from dji_thermal_sdk.dji_sdk import dji_init
from dji_thermal_sdk.utility import rjpeg_to_heatmap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 1) Initialize once (DIRP_SDK_PATH/LD_LIBRARY_PATH should already be set in your venv)
# dji_init()
dji_init(ROOT / "venv/tsdk/utility/bin/linux/release_x64/libdirp.so")

# 2) Use the exact path to your R-JPEG
# img = Path("venv/tsdk/dataset/M3TD/DJI_0001_R.JPG")  # relative to your project root
# or absolute:
img = Path(ROOT / "venv/tsdk/dataset/M3TD/DJI_0001_R.JPG")

# 3) Decode to a float32 °C array
temps = rjpeg_to_heatmap(str(img), dtype="float32")

# 4) Display min/max
print(f"min = {temps.min():.1f} °C   max = {temps.max():.1f} °C")
