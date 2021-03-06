'''
MIT License

Copyright (c) 2019 Arshdeep Bahga and Vijay Madisetti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time 
from datetime import datetime 
from kafka.client import KafkaClient 
from kafka.producer import SimpleProducer 
 
client = KafkaClient("localhost:6667") 

#The following producer will collect messages in batch 
#and send them to Kafka after 20 messages are
# collected or every 60 seconds
                         
producer = SimpleProducer(client,batch_send=True,
            batch_send_every_n=20,
            batch_send_every_t=60)
 
while True: 
    ts=time.time() 
    timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') 
    data = "This is a test string generated at: " + str(timestamp) 
     
    producer.send_messages('test', data) 
 
    time.sleep(1) 
