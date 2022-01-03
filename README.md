# ccb_tool
 A tool to fetch event updates from CCB and push to other services

## Installation
 - Download and extract or use `git clone`.
 - Install requirements with `cd ccb_tool && python -m pip install -r requirements`
 - Edit the values in `example_secrets.py` in the `config` directory and rename to `secrets.py` 
 - Run with `python run_continuously.py` or `python run_once.py` for debugging

### Docker
 If you want to use docker, clone the repo like above and build the image by running `docker build -t ccb_tool .` in the repo directory. Run with `docker run -d --mount type=bind,source=/home/user/.ccb_tool,target=/ccb_tool/config --name ccb_tool ccb_tool` or similar. Place a secrets file in the bound directory following `example_secrets.py`.