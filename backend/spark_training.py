
training_df = spark.read.csv("./data/synthetic_with_anomalies_NEW.csv", header=True, inferSchema=True)
training_df.show(5)
# use UNIX time so it can be an integer
training_df = training_df.withColumn(
    "unix_time", 
    unix_timestamp("time", "yyyy-MM-dd HH:mm:ss.SSS")
)

# Define all categorical fields to index
categorical_cols = ["ip", "method", "path", "referrer", "user_agent"]
indexers = [StringIndexer(inputCol=col, outputCol=col + "_idx", handleInvalid="keep") for col in categorical_cols]

# Update VectorAssembler to include it
assembler = VectorAssembler(
    inputCols=["status", "size", "unix_time"] + [col + "_idx" for col in ["ip", "method", "path", "referrer", "user_agent"]],
    outputCol="features"
)

# note that REQUEST_TYPE = method
# note that REQUEST ARGUMENT = path 

label_indexer = StringIndexer(inputCol="anomalous", outputCol="label")  # for binary classification
# or: StringIndexer(inputCol="category", outputCol="label") for multi-class

print(training_df.columns)

# Combine steps
pipeline = Pipeline(stages=indexers + [assembler, label_indexer])
pipeline_model = pipeline.fit(training_df)
print("Pipeline fit completed")
pipeline_model.save("/data/pipeline_model_2")
print("Pipeline saved")

log_transformed = pipeline_model.transform(training_df)

# show whole dataframe
log_transformed.show(5)

# show features only 
log_transformed.select("features").show(truncate=False)

train_data, test_data = log_transformed.randomSplit([0.8, 0.2], seed=42)

rf = RandomForestClassifier(
    featuresCol="features",
    labelCol="label",
    maxBins=1024  # default is 32, need to override it
)
rf_model = rf.fit(train_data)

predictions = rf_model.transform(test_data)

# Compute AUC
auc_evaluator = BinaryClassificationEvaluator(
    labelCol="label",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
)
auc = auc_evaluator.evaluate(predictions)

# Get predicted label and actual
predicted = predictions.select(
    col("label").cast("integer"),
    col("prediction").cast("integer")
)

# Calculate confusion matrix components
tp = predicted.filter("label = 1 AND prediction = 1").count()
tn = predicted.filter("label = 0 AND prediction = 0").count()
fp = predicted.filter("label = 0 AND prediction = 1").count()
fn = predicted.filter("label = 1 AND prediction = 0").count()

# Derived metrics
accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

# Print all metrics
print(f"AUC:       {auc:.3f}")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")

rf_model.save('/data/random_forest_binary_classifier')