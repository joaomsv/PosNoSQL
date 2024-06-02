sleep 30

mongosh --host router1:27017 <<EOF

    sh.addShard("shard1/shard1a:27018")
    sh.addShard("shard1/shard1b:27018")
    sh.addShard("shard1/shard1c:27018")
EOF