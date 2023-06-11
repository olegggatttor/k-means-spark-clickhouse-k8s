package utils

import org.apache.spark.sql.functions.col
import org.apache.spark.sql.{DataFrame, SparkSession}
import utils.Helpers.DataTransformer

object DataMart {
  private val CLICKHOUSE_URL = "jdbc:clickhouse://clickhouse"
  private val USER = "default"
  private val PASSWORD = ""
  private val DRIVER = "com.clickhouse.jdbc.ClickHouseDriver"
  private val DATA_TABLE = "datasets.openfood"
  private val PREDS_TABLE = "datasets.openfood_predictions"

  def getTrainDataset(): DataFrame = {
    implicit val spark: SparkSession = SparkSession.builder.getOrCreate()
    val colsToKeepStr = Features.features :+ "product_name" :+ "main_category"
    val colsToKeep = colsToKeepStr.map(x => if (x != "product_name" && x != "main_category") col(x).cast("float") else col(x))
    val noNanDf = spark.read
      .format("jdbc")
      .option("driver", DRIVER)
      .option("url", CLICKHOUSE_URL)
      .option("user", USER)
      .option("password", PASSWORD)
      .option("numPartitions", 40)
      .option("dbtable", DATA_TABLE)
      .load()
      .select(colsToKeep:_*)
      .fillNans()

    noNanDf
      .colsToVec(Features.features intersect noNanDf.columns)
      .scaleFeatures()
  }
  
  def writePredictionsToClickhouse(preds: DataFrame): Unit = {
    preds.write
      .format("jdbc")
      .mode("append")
      .option("driver", DRIVER)
      .option("url", CLICKHOUSE_URL)
      .option("user", USER)
      .option("password", PASSWORD)
      .option("dbtable", PREDS_TABLE).save()
  }
}
