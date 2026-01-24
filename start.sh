#!/bin/bash

LOG_DIR='/data/logs'

mkdir -p "$LOG_DIR"

LOG_FILE1="$LOG_DIR/info.log"

if [ ! -f "$LOG_FILE1" ]; then
    touch "$LOG_FILE1"
fi

nohup python3 /app/manage.py runserver 0.0.0.0:9876 >> "$LOG_FILE1" 2>&1 &

tail -50f "$LOG_FILE1" 