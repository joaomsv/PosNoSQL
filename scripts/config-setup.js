rs.initiate(
   {
      _id: "config-server",
      configsvr: true,
      version: 1,
      members: [
         { _id: 0, host : "config1:27017", priority: 2},
         { _id: 1, host : "config2:27017", priority: 1},
         { _id: 2, host : "config3:27017", priority: 0}
      ]
   }
)
