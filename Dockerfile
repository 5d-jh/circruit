FROM python:3.7

EXPOSE 5000

WORKDIR /circruit
COPY . /circruit

ENV PYTHONPATH /circruit
ENV STATIC_URL /static
ENV STATIC_PATH /circruit/static
ENV DATABASE_URL mongodb://circruitdb:FK7QSRVGwYoKObRfSRjdycTSjXluNvrKaOiMhgzX4GbmuaR51QZX5UCHBlBeYA3ogEhvy2XqeoyPEpUoj2OS5g==@circruitdb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb

RUN pip install -r requirements.txt
CMD ["uwsgi", "--ini", "uwsgi.ini"]