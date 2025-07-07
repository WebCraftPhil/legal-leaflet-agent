#!/bin/bash
curl -X POST http://127.0.0.1:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Protect your time and energy as a freelancer with a proper contract before you start working for a client – a vibrant sunset over a calm ocean, in a minimalist style",
    "api_key": "supersecretkey123"
  }'
