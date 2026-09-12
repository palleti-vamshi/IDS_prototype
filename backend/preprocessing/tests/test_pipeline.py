from backend.preprocessing.pipeline import DatasetPipeline


pipeline = DatasetPipeline()

try:
    pipeline.start()

    # Keep the pipeline alive so the MQTT collector
    # can receive and process messages.
    input("Press Enter to stop the dataset pipeline...\n")

finally:
    pipeline.stop()