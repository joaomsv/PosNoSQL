rs.initiate(
    {
       _id: "shard3",
       version: 1,
       members: [
          { _id: 0, host : "shard3a:27020" },
          { _id: 1, host : "shard3b:27020" },
          { _id: 2, host : "shard3c:27020" }
       ]
    }
)