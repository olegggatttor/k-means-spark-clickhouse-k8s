import argparse
from pyspark.sql import SparkSession

from preprocessing.load_data import load, write_ch
from model import PySparkKMeans


def main(spark, dbtable: str, save_path: str, params: dict):
    df = load(spark, dbtable)
    trainer = PySparkKMeans(df, params)
    trainer.train()

    preds = trainer.predict(df).select("prediction")
    write_ch(preds, "datasets.openfood_predictions")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", default="datasets.openfood", required=False)
    parser.add_argument("--save_path", default="../data/openfood_kmeans.model", required=False)
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
                .getOrCreate()

    main(spark, args.train_path, args.save_path, {"k": args.k, "max_iter": args.max_iter})
