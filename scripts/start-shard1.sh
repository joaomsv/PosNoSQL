sleep 5

mongosh --host shard1a:27018 <<EOF

    load('./scripts/shard1-setup.js')
EOF