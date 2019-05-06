FROM python:3
WORKDIR /app
ADD . /app
RUN pip install flask
RUN pip install envparse
RUN pip install beautifulsoup4
RUN pip install schedule
CMD [ "python", "./app.py" ]