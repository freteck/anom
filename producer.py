import time
import json
from time import sleep
from json import dumps
from kafka import KafkaProducer
import re


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
    for i in range(1, 10000):
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                data_dict = to_dict(line.strip())
                key = str(i) 
                
                # Skip lines that do not match format
                if data_dict is None: 
                    # print(f"Skipping line {i}: {line.strip()}")
                    continue  
                
                kafka_producer.send('topic_test', key=key, value=data_dict)
                print(f"Sending data to Kafka: {key}, {data_dict}") 
                time.sleep(0.1)  

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8'),
    key_serializer=lambda x: x.encode('utf-8')
)

stream_file_lines("archive/short.access.log", producer)