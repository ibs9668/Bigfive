#!/bin/bash

while ((1)); do
    date
    python3 cal_group.py >> cal_group.log
    sleep 300
done
