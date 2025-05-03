# CS5614: Final Project (Anomaly Detection)

Run the following commands to get started. We assume you have python 3.0+ set up on your machine.

```source ./venv/bin/activate```

If on Mac:
```make start-mac```

Otherwise:
```make start```

*Note: If you receive the error "Cannot connect to the Docker daemon at {LOCATION}. Is the docker daemon running?" Then docker has not been started on your machine. Launch the docker application to resolve.

Wait for the docker containers to start, then run:

```python ./producer.py```

If all goes well you should see the following output
```
Sent 1 dummy value(s) to topic_test
Sent 2 dummy value(s) to topic_test
Sent 3 dummy value(s) to topic_test
...
```
