from fastapi import FastAPI, BackgroundTasks
import time
from time import sleep
from json import dumps
from kafka import KafkaProducer
from threading import Thread, Event
import re

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    key_serializer=lambda x: x.encode('utf-8')
)

streaming_thread = None
stream_stop_event = Event()

def to_dict(line):
    pattern = (
        r'(?P<ip_address>\S+) - - '
        r'\[(?P<date_time>[^\]]+)\] '
        r'"(?P<request_type>\S+) (?P<request_arg>[^"]+?)" '
        r'(?P<status_code>\d{3}) '
        r'(?P<response_size>\d+|-) ' # in case of no response size, it will be '-'
        r'"(?P<referrer>[^"]*)" ' # use * in case of empty ""
        r'"(?P<user_agent>[^"]*)"'
    )
    
    match = re.match(pattern, line)
    if not match:
        return None
    
    result = match.groupdict()
    
    # convert response_size to int if it's not '-'
    if result['response_size'] != '-':
        result['response_size'] = int(result['response_size'])
    else:
        result['response_size'] = None
    
    # convert status_code to int
    result['status_code'] = int(result['status_code'])
    
    return result

def stream_file_lines(filename, kafka_producer):
  with open(filename, 'r') as f:
    for i, line in enumerate(f):
      if stream_stop_event.is_set():
        break

      data_dict = to_dict(line.strip())
      key = str(i) 
      
      # Skip lines that do not match format
      if data_dict is None: 
          # print(f"Skipping line {i}: {line.strip()}")
          continue  
      
      kafka_producer.send('topic_test', key=key, value=data_dict)
      print(f"Sending data to Kafka: {key}, {data_dict}") 
      time.sleep(0.1)
    producer.flush()
    print("Stream ended")


@app.get("/start-streaming/")
async def start_streaming(filename: str = "access.log"):
  global producer
  global streaming_thread
  global stream_stop_event
  if streaming_thread and streaming_thread.is_alive():
      return {"status": "Already streaming"}
  stream_stop_event.clear()
  streaming_thread = Thread(target=stream_file_lines, args=("../archive/synthetic_with_anomalies.access.log", producer))
  streaming_thread.start()
  return {"status": "Streaming started in background"}

@app.get("/stop-streaming/")
async def stop_streaming():
  global streaming_thread
  global stream_stop_event
  global producer

  stream_stop_event.set()
  if streaming_thread:
    streaming_thread.join(timeout=5)
    if streaming_thread.is_alive():
      return {"status": "Thread failed to stop in time"}
    return {"status": "Stopped"}
  