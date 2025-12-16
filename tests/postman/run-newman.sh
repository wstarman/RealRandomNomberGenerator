#!/bin/bash
newman run tests/postman/rng-api.postman_collection.json \
  --env-var "baseUrl=http://127.0.0.1:8000" \
  --reporters cli,json \
  --reporter-json-export tests/postman/results.json
