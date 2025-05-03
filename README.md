# CS5614 Assignment 4

Run the following commands to get started. We assume you have python 3.0+ set up on your machine.

```python -m pip install kafka-python```

```docker compose -f ./docker-compose-expose.yml up --detach```

Wait for the docker containers to start, then run:

```python ./producer.py```

If all goes well you should see the following output
```
Sent 1 dummy value(s) to topic_test
Sent 2 dummy value(s) to topic_test
Sent 3 dummy value(s) to topic_test
...
```
