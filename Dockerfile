FROM python:3.8

COPY manage.py gunicorn-cfg.py requirements.txt cron-django-entrypoint.sh ./
COPY core core
COPY routers routers
COPY data_utilities data_utilities
COPY datasets datasets
COPY elastic elastic
COPY anomaly_detection anomaly_detection

RUN pip install -r requirements.txt

COPY cron_3.0pl1-137_amd64.deb ./
RUN dpkg -i cron_3.0pl1-137_amd64.deb

RUN mkdir logs
RUN touch logs/onenet_dashboard.log
RUN touch logs/cronjob.log

RUN chmod 777 /cron-django-entrypoint.sh

EXPOSE 5005
ENTRYPOINT ["./cron-django-entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
