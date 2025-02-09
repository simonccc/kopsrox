#!/usr/bin/env bash
kill -9 $(cat PID)
python3 -m http.server -b "::"  > log.txt 2>&1 &
echo $! > PID
