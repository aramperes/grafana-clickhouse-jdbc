# grafana-clickhouse-jdbc

Consolidate your JDBC data in ClickHouse, and visualize with Grafana.

![Screenshot](.github/grafana.png)

## Motivations

1. The generic JDBC datasource and some databases like Oracle are only supported in Grafana Enterpise. On the other hand, ClickHouse has an open-source plugin and can speak JDBC to other databases.
2. For expensive JOINs, it makes sense to mirror the data to ClickHouse to take advantage of its analytical capabilities. It makes this easy with `JDBC` tables and `LIVE VIEW`.
For streaming data, ClickHouse also supports materializing Kafka and AMQP topics.

## Components

- [Postgres](https://github.com/postgres/postgres): Holds the raw data. This can be any JDBC-compatible database (and you can have multiple databases).
- [ClickHouse](https://github.com/ClickHouse/ClickHouse): Mirrors the data from Postgres/JDBC and stores the data locally using a `LIVE VIEW` that refreshes every X seconds.
- [ClickHouse JDBC Bridge](https://github.com/ClickHouse/clickhouse-jdbc-bridge): Bridge required for ClickHouse to speak JDBC (includes vendor drivers for Postgres etc.)
- [Grafana](https://github.com/grafana/grafana): Reads data from ClickHouse using the [ClickHouse Datasource Plugin](https://github.com/grafana/clickhouse-datasource), and visualizes using graphs.

See `infra/docker-compose.yaml` for the images and environment variables.

## Live Views

The usage of [`LIVE VIEW`](https://clickhouse.com/docs/en/sql-reference/statements/create/view#live-view-experimental) is optional, and this feature is currently marked experimental in ClickHouse. I would only recommend using it on tables that need to be joined with other data, as this is a nice way to cache the data in ClickHouse. Otherwise, you can just make Grafana read the JDBC tables directly.

This repo uses `LIVE VIEW` to periodically pull data from the JDBC tables into ClickHouse memory. I couldn't find a better way to localize the data. Ideally, this would be storing the data on dist to reduce disk pressure. There is a [ClickHouse feature request](https://github.com/ClickHouse/ClickHouse/issues/33919) to add refreshes to `MATERIALIZED VIEW`, which would allow configuring a table engine for the data.

If your data can be streamed to Kafka or RabbitMQ, it is possible to build a `MATERIALIZED VIEW` that gets appended with new data: there's decent [documentation](https://clickhouse.com/docs/en/integrations/kafka) on this architecture. Note that this wouldn't support deletions (you could append updates and use a `ReplacingMergeTree`). This would be a good idea if your data cannot fit in ClickHouse memory with a `LIVE VIEW`.

## Example

This repo uses data pulled from Hacker News to demonstrate the stack. Python scripts in `services` will scrape HN and push the data into 2 Postgres tables (`comments` and `stories`).

The sample service does not interact with ClickHouse directly, to demonstrate how the Grafana/ClickHouse combination is entirely separated from the dev stack.

The sample Grafana dashboard (screenshot) does multiple ClickHouse queries, one of which is a `JOIN` between the two materialized views. Can you guess which one?
