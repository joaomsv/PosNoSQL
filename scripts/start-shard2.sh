sleep 5

mongosh --host shard2a:27019 <<EOF

    load('./scripts/shard2-setup.js')
EOF