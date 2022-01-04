# ccb_tool
 A tool to fetch event updates from CCB and push to other services

## Installation
 - Download and extract or use `git clone`.
 - Install requirements with `cd ccb_tool && python -m pip install -r requirements`
 - Edit the values in `example_secrets.py` in the `config` directory and rename to `secrets.py` 
 - Run with `python run_continuously.py` or `python run_once.py` for debugging

## Docker Installation
 - Clone the repo like above
 - Build the image by running `docker build -t ccb_tool .` in the repo directory
 - Run with `docker run -d -i -t --mount type=bind,source=/home/user/.ccb_tool,target=/ccb_tool/config --name ccb_tool ccb_tool` or similar. Place a `secrets.py` file in the bound directory following the scheme of `example_secrets.py`.
