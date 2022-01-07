# ccb_tool
 CCB_Tool is a tool that pulls modified events from CCB on a regular basis and updates Asana tasks based on their changes. Events are filtered by event type or resources before being passed on to Asana. CCB_Tool also adds tags to indicate task status (modified, new) and notify the user of changes, as well as indicate which venue resources the event has. Event tasks are sorted by event type into sections on creation

## Features
 - Customizable polling frequency
 - Custom date range polls
 - Event filtering by venue 
 - Event sorting and filtering by event type (one-time, recurring)
 - Task change notifications by tag (new, modified)
 - Customizable subtasks copied from template task
 - Customizable additional fields reported in task description
 - Event venue indicated by tag
 - Robust API handling (pagination, return confirmation)
 - Email error reporting
 - Docker image
 - Separate credential handling

## Linux Installation
 - Download and extract or use `git clone`.
 - Install python requirements with `python -m pip install -r requirements` in the repo directory.
 - Edit the values in `example_secrets.py` in the `config` directory and rename to `secrets.py`. 
 - Run with `python run_continuously.py` or `python run_once.py` for debugging.

## Linux Docker Installation
 It's a relatively standard Docker build but it needs a bind mount to supply the `secrets.py`.
 - [Install](https://docs.docker.com/engine/install/) docker if it isn't already
 - Clone the repo like above.
 - Build the image by running `docker build -t ccb_tool .` in the repo directory.
 - Create a config directory with `mkdir ~/.ccb_tool` for example
 - Run with `docker run -d -i -t --mount type=bind,source=/home/$(whoami)/.ccb_tool,target=/ccb_tool/config --restart unless-stopped --name ccb_tool ccb_tool` or similar. Override the `TZ` env variable if necessary. Defaults to `America/Chicago`. 
 - Place a `secrets.py` file in the bound directory following the scheme of `example_secrets.py`.
 - `docker container restart ccb_tool` to restart the container after config change.
