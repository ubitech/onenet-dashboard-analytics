#!/bin/bash
echo "The script name : $0"
echo "The first argument :  $1"

# Cron

if [ "$1" = cron ]; then
  env >> /etc/environment
  # service cron restart
  python manage.py crontab add
fi


exec "$@"
