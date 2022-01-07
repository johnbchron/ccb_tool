# ccb_tool
 A tool to fetch event updates from CCB and push to other services

## Installation
 - Download and extract or use `git clone`.
 - Install python requirements with `python -m pip install -r requirements` in the repo directory.
 - Edit the values in `example_secrets.py` in the `config` directory and rename to `secrets.py`. 
 - Run with `python run_continuously.py` or `python run_once.py` for debugging.

## Docker Installation
 It's a relatively standard Docker build but it needs a bind mount to supply the `secrets.py`.
 - [Install](https://docs.docker.com/engine/install/) docker if it isn't already
 - Clone the repo like above.
 - Build the image by running `docker build -t ccb_tool .` in the repo directory.
 - Create a config directory with `mkdir ~/.ccb_tool` for example
 - Run with `docker run -d -i -t --mount type=bind,source=/home/user/.ccb_tool,target=/ccb_tool/config --restart unless-stopped --name ccb_tool ccb_tool` or similar. Override the `TZ` env variable if necessary. Defaults to `America/Chicago`. 
 - Place a `secrets.py` file in the bound directory following the scheme of `example_secrets.py`.
 - `docker container restart ccb_tool` to restart the container after config change.
