# ── 1) Base image with Python 3.12
FROM python:3.12-slim

# ── 2) Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl unzip && \
    rm -rf /var/lib/apt/lists/*

# ── 3) Download & unpack the DJI Thermal SDK
#     (replace URL with the current “Linux v1.7 zip” link)
ENV TSDK_URL="https://terra-1-g.djicdn.com/2640963bcd8e45c0a4f0cb9829739d6b/TSDK/v1.7%2812.0-WA345T%29/dji_thermal_sdk_v1.7_20241205.zip"
RUN mkdir -p /opt/tsdk && cd /opt/tsdk && \
    curl -L "$TSDK_URL" -o tsdk.zip && \
    unzip tsdk.zip && \
    mv tsdk-core/* . && rmdir tsdk-core tsdk.zip

# ── 4) Set library path for ctypes
ENV DIRP_SDK_PATH=/opt/tsdk/utility/bin/linux/release_x64/libdirp.so
ENV LD_LIBRARY_PATH=/opt/tsdk/utility/bin/linux/release_x64

# ── 5) Install Python deps
COPY decode.py /usr/local/bin/decode.py
RUN pip install --no-cache-dir \
      numpy tifffile dji-thermal-sdk

# ── 6) Make the script executable and set entrypoint
RUN chmod +x /usr/local/bin/decode.py
ENTRYPOINT ["decode.py"]
CMD ["--help"]
