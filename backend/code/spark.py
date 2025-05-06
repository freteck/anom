from pyspark.sql import SparkSession
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql.functions import col, when, from_json, unix_timestamp, coalesce, to_timestamp, lit
from pyspark.sql.types import StructType, StructField, BooleanType, LongType, IntegerType, StringType
import time

spark = SparkSession.\
        builder.\
        appName("pyspark-kafka-streaming").\
        master("spark://spark-master:7077").\
        config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0"). \
        config("spark.executor.memory", "512m").\
        getOrCreate()


df_streamed_raw = (spark.readStream.format("kafka")
                   .option("kafka.bootstrap.servers", "kafka:9093")
                   .option("subscribe", "topic_test")
                   .option("startingOffsets", "earliest")  # Ensure you are reading from the earliest offset
                   .load())

# convert byte stream to string
df_streamed_kv = (df_streamed_raw
    .withColumn("key", df_streamed_raw["key"].cast(StringType()))
    .withColumn("value", df_streamed_raw["value"].cast(StringType())))

event_schema = StructType([
    StructField("ip_address", StringType()),
    StructField("date_time", StringType()),
    StructField("request_type", StringType()),
    StructField("request_arg", StringType()),
    StructField("status_code", StringType()),
    StructField("response_size", StringType()),
    StructField("referrer", StringType()),
    StructField("user_agent", StringType())
])

# Parse the events from JSON format
df_parsed = (df_streamed_kv
           # Sets schema for event data
           .withColumn("value", from_json("value", event_schema))
          )

df_formatted = (df_parsed.select(
    col("key").alias("event_key")
    ,col("topic").alias("event_topic")
    ,col("timestamp").alias("event_timestamp")
    ,col("value.ip_address").alias("ip_address")
    ,col("value.date_time").alias("date_time")
    ,col("value.request_type").alias("request_type")
    ,col("value.request_arg").alias("request_arg")
    ,col("value.status_code").alias("status_code")
    ,col("value.response_size").cast(IntegerType()).alias("response_size")
    ,col("value.referrer").alias("referrer")
    ,col("value.user_agent").alias("user_agent")
))

# # Write the parsed data to console
query = (df_formatted.writeStream.format("console").outputMode("append").trigger(processingTime='5 seconds').start())

# Print the name of active streams (This may be useful during debugging)
for s in spark.streams.active:
    print(f"ID:{s.id} | NAME:{s.name}")

# query.stop()

kafka_timestamp_format = "dd/MMM/yyyy:HH:mm:ss Z"

# Convert date_time from string to timestamp using the correct format
df_formatted = df_formatted.withColumn(
    "event_time",
    coalesce(
        to_timestamp(col("date_time"), kafka_timestamp_format),
    )
)

# Filter out rows where timestamp parsing failed (resulted in null)
df_formatted = df_formatted.filter(col("event_time").isNotNull())

# create windows
windowed_df = df_formatted.withWatermark("event_time", "10 seconds")

# adjust names to match the dataset used for training
renamed_df = windowed_df.selectExpr(
    "ip_address as ip",
    "request_type as method",
    "request_arg as path",
    "status_code as status",
    "response_size as size",
    "referrer",
    "user_agent",
    "event_time"
)

# convert data to ints and calculate unix_time
renamed_df = renamed_df \
    .withColumn("status", coalesce(col("status").cast("int"), lit(0))) \
    .withColumn("size", coalesce(col("size").cast("int"), lit(0))) \
    .withColumn("unix_time", unix_timestamp("event_time"))

# Filter again for safety before applying models, ensuring unix_time is not null
renamed_df = renamed_df.filter(col("unix_time").isNotNull())

# Load transformation pipeline and classifier
pipeline_model = PipelineModel.load("./data/models/pipeline_model_1")
rf_model = RandomForestClassificationModel.load("./data/models/random_forester_binary_classifier")
transformed_df = pipeline_model.transform(renamed_df)

# make predictions
predictions = rf_model.transform(transformed_df)

# Get only anomalies
anomalies_df = predictions.filter(col("prediction") == 1.0)

# Print full rows if anomalies are detected
query = anomalies_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.stop()
