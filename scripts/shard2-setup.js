rs.initiate(
    {
       _id: "shard2",
       version: 1,
       members: [
          { _id: 0, host : "shard2a:27019" },
          { _id: 1, host : "shard2b:27019" },
          { _id: 2, host : "shard2c:27019" }
       ]
    }
)