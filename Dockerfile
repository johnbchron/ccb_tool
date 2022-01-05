FROM python:3.9.1
ADD . /ccb_tool
WORKDIR /ccb_tool
RUN pip install -r requirements.txt
ENV TZ "America/Chicago"
CMD [ "python", "./run_continuously.py" ]
