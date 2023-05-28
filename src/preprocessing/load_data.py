CLICKHOUSE_URL = "jdbc:clickhouse://clickhouse"
USER = "default"
PASSWORD = ""
DRIVER = "com.clickhouse.jdbc.ClickHouseDriver"


def load(spark, dbtable):
    return spark.read.format('jdbc') \
        .option('driver', DRIVER) \
        .option('url', CLICKHOUSE_URL) \
        .option('user', USER) \
        .option('password', PASSWORD) \
        .option("numPartitions", 40) \
        .option('dbtable', dbtable).load()


def write_ch(data, dbtable):
    return data.write.format('jdbc') \
        .mode("append") \
        .option('driver', DRIVER) \
        .option('url', CLICKHOUSE_URL) \
        .option('user', USER) \
        .option('password', PASSWORD) \
        .option('dbtable', dbtable).save()
