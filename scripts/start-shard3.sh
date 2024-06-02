sleep 5

mongosh --host shard3a:27020 <<EOF

    load('./scripts/shard3-setup.js')
EOF