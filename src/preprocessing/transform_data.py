from pyspark.ml.feature import VectorAssembler, MinMaxScaler
from pyspark.sql.functions import isnull, when, count, col, lit, sum
import typing as tp
from .constants import NUM_COLS
from pyspark.sql import DataFrame


def __fill_nans(df: DataFrame, filter_null_cols_border: int) -> DataFrame:
    nan_percentage = df.select([(lit(100) * count(when(isnull(c), c)) / count("*")).alias(c) for c in df.columns]) \
        .collect()[0].asDict()
    non_nulls_cols = [k for k, v in nan_percentage.items() if v < filter_null_cols_border]

    df = df.select(non_nulls_cols)
    df = df.na.fill(0.0).na.fill("unk")
    return df


def __cols_to_vec(df: DataFrame, input_features: tp.List[str]) -> DataFrame:
    return VectorAssembler(inputCols=input_features, outputCol="raw_features").setHandleInvalid("error").transform(df)


def __scale_features(df: DataFrame) -> DataFrame:
    scaler = MinMaxScaler().setInputCol("raw_features").setOutputCol("features")
    scaler_model = scaler.fit(df)
    return scaler_model.transform(df)


def transform(df: DataFrame, filter_null_cols_border=40) -> DataFrame:
    print("START TRANSFORM")
    cols_to_keep = [col("product_name"), col("main_category")] + [col(x).cast("float") for x in NUM_COLS]
    df = df.select(cols_to_keep)

    df = __fill_nans(df, filter_null_cols_border)
    df = __cols_to_vec(df, list(set(NUM_COLS) & set(df.columns)))
    df = __scale_features(df)

    print("END TRANSFORM")
    return df


__all__ = ['transform']
