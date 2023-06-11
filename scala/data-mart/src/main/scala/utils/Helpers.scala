package utils

import org.apache.spark.ml.feature.{MinMaxScaler, VectorAssembler}
import org.apache.spark.sql.functions.{col, count, isnan, isnull, lit, when}
import org.apache.spark.sql.{DataFrame, SQLContext}

object Helpers {
  implicit class DataTransformer(df: DataFrame) {
    def fillNans(): DataFrame = {
      val notNanCols = df.select(df.columns.map { colName =>
        (lit(100.0) * count(when(isnull(col(colName)) || isnan(col(colName)), colName)) / count("*")) as colName
      }:_*).collect.head.getValuesMap[Double](df.columns).filter { case (k, v) => v < 40 }.keys.map(x => col(x)).toSeq

      df
        .select(notNanCols:_*)
        .na.fill(0.0)
        .na.fill("unk")
    }

    def colsToVec(inputFeatures: Seq[String]): DataFrame = {
      new VectorAssembler()
        .setInputCols(inputFeatures.toArray)
        .setOutputCol("raw_features")
        .setHandleInvalid("error")
        .transform(df)
    }

    def scaleFeatures(): DataFrame = {
      val scaler = new MinMaxScaler().setInputCol("raw_features").setOutputCol("features")
      val scalerModel = scaler.fit(df)
      scalerModel.transform(df)
    }


  }
}
