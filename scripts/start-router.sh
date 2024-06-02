sleep 20

mongosh --host router1:27017 <<EOF

    sh.addShard("shard1/shard1a:27018")
    sh.addShard("shard1/shard1b:27018")
    sh.addShard("shard1/shard1c:27018")
    sh.addShard("shard2/shard2a:27019")
    sh.addShard("shard2/shard2b:27019")
    sh.addShard("shard2/shard2c:27019")
    sh.addShard("shard3/shard3a:27020")
    sh.addShard("shard3/shard3b:27020")
    sh.addShard("shard3/shard3c:27020")
EOF