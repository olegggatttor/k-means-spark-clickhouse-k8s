import argparse
from pyspark.sql import SparkSession, SQLContext, DataFrame
from model import PySparkKMeans


def main(spark, params: dict):
    sc = spark.sparkContext
    sqlContext = SQLContext(spark)
    jvm_df = sc._jvm.utils.DataMart.getTrainDataset()
    df = DataFrame(jvm_df, sqlContext)

    trainer = PySparkKMeans(df, params)
    trainer.train()

    preds = trainer.predict(df).select("prediction")

    sc._jvm.utils.DataMart.writePredictionsToClickhouse(preds._jdf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", default=2, required=False)
    parser.add_argument("--max_iter", default=5, required=False)
    args = parser.parse_args()

    spark = SparkSession.builder \
                .appName("openfood-trainer") \
                .master("local[*]") \
                .config("spark.driver.cores", "8") \
                .config("spark.driver.memory", "4g") \
                .config("spark.executor.memory", "10g") \
                .config("spark.driver.extraClassPath", "jars/clickhouse-jdbc-0.4.6-all.jar") \
                .config("spark.jars", "scala/data-mart/target/scala-2.12/data-mart_2.12-0.1.0-SNAPSHOT.jar") \
                .getOrCreate()

    main(spark, {"k": args.k, "max_iter": args.max_iter})
