FROM python:3.7

EXPOSE 5000
EXPOSE 27017

WORKDIR /circruit
COPY . /circruit

ENV FLASK_ENV production
ENV PYTHONPATH /circruit
ENV STATIC_URL /static
ENV STATIC_PATH /circruit/app/static
ENV DATABASE_URL mongodb://172.25.0.1
ENV OAUTHLIB_INSECURE_TRANSPORT 1

RUN pip install -r requirements.txt
CMD ["uwsgi", "--ini", "uwsgi.ini"]