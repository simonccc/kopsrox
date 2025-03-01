#!/usr/bin/env bash
kill -9 $(cat PID) > /dev/null 2>&1
python3 -m http.server -b "::"  > log.txt 2>&1 &
echo $! > PID
