**Day 5 of 77: Read replicas**

**What it is.** A read replica is a copy of your primary database that serves `SELECT`s while the primary handles writes. Changes flow one way: primary → replica(s), usually asynchronously. Apps (or a proxy) route reads to replicas and writes to the primary.

**Why it exists.** Write load and read load don't scale the same way. Most apps read far more than they write. Adding RAM or a bigger primary helps until it doesn't; replicas let you add read capacity horizontally without making every write wait on more machines. They also give you a warm standby for failover and a place to run heavy analytics without hammering the OLTP primary.

**Real example.** An e-commerce site on Postgres: the primary takes orders and inventory updates. Two streaming replicas (built-in physical replication) sit behind a load balancer for product pages, search, and order-history views. The app uses a read/write split in the connection pool: `INSERT`/`UPDATE` go to the primary; `SELECT`s go to the replica pool. After a write, the app either reads from the primary for a short window or waits until the replica's LSN catches up if it needs the brand-new row.

**Trade-off.** Replication lag. Asynchronous replicas can be seconds (or worse under load) behind the primary, so a user who just placed an order might not see it on the next page if that page hits a lagging replica. Synchronous replication removes that surprise but slows every commit. You also pay for extra storage and network, and replicas don't magically fix a bad query plan—they multiply its cost across more machines if you aren't careful.

**Related.** Leader–follower replication is the topology under most read replicas; eventual consistency is what clients feel when lag shows up.
