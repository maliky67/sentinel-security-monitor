# Final Results — Batched Persistence Optimization

**Date:** October 30, 2026

Session 8 concluded with a significant performance improvement to Sentinel's SQLite persistence layer.

The original implementation relied on individual SQLAlchemy existence checks and frequent flush operations. Profiling demonstrated that these operations dominated processing time.

A staged optimization approach was implemented:

1. Suppressed unnecessary automatic session flushes.
2. Introduced bounded batch existence checks.
3. Implemented batched event, alert, and evidence persistence.

# Measured results

| Workload | Original persistence | Optimized persistence | Speedup |
| --- | ---: | ---: | ---: |
| 600-event attack | 1.1124 s | 0.0996 s | 11.2× |
| 10,000-record mixed | 8.8440 s | 0.5481 s | 16.1× |

The mixed workload's end-to-end throughput increased from approximately 1,084 to 10,653 records per second.

The optimized mixed workload produced 300 AUTH-001 alerts and 300 AUTH-002 alerts, with 9,000 accepted and 1,000 rejected input records.

Peak traced allocations during mixed-workload persistence decreased from 23.54 MiB after the initial no-autoflush optimization to 2.48 MiB after batching.

# Engineering conclusions

The primary bottleneck was SQLAlchemy session and per-record query overhead rather than the detection engine.

Bounded batch persistence substantially improved performance while preserving the expected outputs in the benchmark scenarios.

# Limitations

Results reflect synthetic batch workloads on a local SQLite database. Performance under concurrent writers, continuous ingestion, and production infrastructure remains untested.

The next development phase should address dashboard and CLI test coverage, extended stress tests, and production-readiness verification.
