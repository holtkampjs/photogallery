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

import boto3
import json

AWS_KEY="<enter>"
AWS_SECRET="<enter>"
REGION="us-east-1"
BUCKET = "cloudcomputingcourse2019"

s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,
                        aws_secret_access_key=AWS_SECRET)

cors_configuration={
        'CORSRules': [
            {
                'AllowedHeaders': [
                    '*',
                ],
                'AllowedMethods': [
                    'PUT','POST','DELETE'
                ],
                'AllowedOrigins': [
                    'http://www.example.com',
                ],
                'ExposeHeaders': [
                    'x-amz-server-side-encryption', 
                    'x-amz-request-id', 'x-amz-id-2'
                ],
                'MaxAgeSeconds': 3000
            },
        ]

s3.put_bucket_cors(Bucket=BUCKET, CORSConfiguration=cors_configuration)