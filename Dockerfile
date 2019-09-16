FROM python:3.7
COPY requirements.txt /
COPY gunicorn.conf /
RUN pip install gunicorn
RUN pip install -r requirements.txt
COPY server.py /
CMD [ "gunicorn", "-c", "gunicorn.conf", "server:app" ]
