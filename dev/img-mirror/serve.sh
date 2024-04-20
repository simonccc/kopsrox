#!/usr/bin/env bash
if [ ! -f s.pid ] 
then
  python3 -m http.server -b "::" >> serve.log &
  echo $! > s.pid
  exit
fi
echo 'pid found'
