#!/bin/bash
while ((1)); do
    date
    python cal_group.py >> cal_group.log
    sleep 300
done