#!/bin/bash
for i in $(seq 1 100); do
 curl -X 'POST' \
  'http://13.239.4.143:8000/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Message": "string12345"}'
done