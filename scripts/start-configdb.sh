#!/bin/bash

# docker-compose up -d

sleep 5

mongosh --host config1:27017 <<EOF

    load('./scripts/config-setup.js')
EOF