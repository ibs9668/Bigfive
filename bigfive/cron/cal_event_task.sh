#!/bin/bash

while ((1)); do
    date
    python3 cal_event_task.py >> cal_event_task.log
    sleep 300
done
