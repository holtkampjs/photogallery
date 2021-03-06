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

#!flask/bin/python
from distutils.log import error
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect, session
import os
import boto3
import time
import datetime
from boto3.dynamodb.conditions import Key, Attr
import exifread
import json

app = Flask(__name__, static_url_path="")
app.secret_key = 'foo'

UPLOAD_FOLDER = os.path.join(app.root_path,'media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
AWS_ACCESS_KEY="AKIAUDOK4ZBBZ5ONKO7X"
# AWS_SECRET_KEY="<enter>+0vqOmhI3ObEtIvQ+jmAkh/"
AWS_SECRET_KEY="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"
REGION="us-east-1"
BUCKET_NAME="elasticbeanstalk-us-east-1-282282739779"

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name=REGION)

table = dynamodb.Table('PhotoGallery')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def getExifData(path_name):
    f = open(path_name, 'rb')
    tags = exifread.process_file(f)
    ExifData={}
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail',
                        'TIFFThumbnail',
                        'Filename',
                        'EXIF MakerNote'):
            key="%s"%(tag)
            val="%s"%(tags[tag])
            ExifData[key]=val
    return ExifData

def s3uploading(filename, filenameWithPath):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY)

    bucket = BUCKET_NAME
    path_filename = "photos/" + filename
    print(path_filename)
    s3.upload_file(filenameWithPath, bucket, path_filename)
    s3.put_object_acl(ACL='public-read',
                Bucket=bucket, Key=path_filename)
    return "http://"+BUCKET_NAME+\
        ".s3-website-us-east-1.amazonaws.com/"+ path_filename

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if not 'username' in session:
        return redirect('/login')

    response = table.scan(
        FilterExpression=Attr('username').eq(session['username'])
    )

    items = response['Items']
    print(items)

    return render_template('index.html', photos=items)

@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    if request.method == 'POST':
        uploadedFileURL=''

        file = request.files['imagefile']
        title = request.form['title']
        tags = request.form['tags']
        description = request.form['description']

        print(title,tags,description)
        if file and allowed_file(file.filename):
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER,
                                        filename)
            print(filenameWithPath)
            file.save(filenameWithPath)
            uploadedFileURL = s3uploading(filename,
                                        filenameWithPath);
            ExifData=getExifData(filenameWithPath)
            ts=time.time()
            timestamp = datetime.datetime.\
                        fromtimestamp(ts).\
                        strftime('%Y-%m-%d %H:%M:%S')

            table.put_item(
            Item={
                    "PhotoID": str(int(ts*1000)),
                    "CreationTime": timestamp,
                    "Title": title,
                    "username": session['username'],
                    "Description": description,
                    "Tags": tags,
                    "URL": uploadedFileURL,
                    "ExifData": json.dumps(ExifData)
                }
            )

        return redirect('/')
    else:
        return render_template('form.html')

@app.route('/<int:photoID>', methods=['GET'])
def view_photo(photoID):
    if not 'username' in session:
        return redirect('/')

    response = table.scan(
        FilterExpression=Attr('PhotoID').eq(str(photoID))
    )

    items = response['Items']
    print(items[0])
    tags=items[0]['Tags'].split(',')
    exifdata=json.loads(items[0]['ExifData'])

    return render_template('photodetail.html',
            photo=items[0], tags=tags, exifdata=exifdata)

@app.route('/search', methods=['GET'])
def search_page():
    if not 'username' in session:
        return redirect('/')

    query = request.args.get('query', None)

    response = table.scan(
        FilterExpression=(Attr('Title').contains(str(query)) |
                        Attr('Description').contains(str(query)) |
                        Attr('Tags').contains(str(query))) &
                        Attr('username').eq(session['username'])
    )
    items = response['Items']
    return render_template('search.html',
            photos=items, searchquery=query)

@app.route('/signup')
def signup():
    if 'username' in session:
        return redirect('/')
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_repeat = request.form['psw-repeat']

        if password == password_repeat:
            user_table = dynamodb.Table('users')
            ts=time.time()
            user_table.put_item(
                Item={
                    'userID': str(int(ts*1000)),
                    'username': username,
                    'password': password
                }
            )
            if 'username' in session:
                session.pop('username', None)
            return redirect('/login')
    return render_template('signup.html', error="Passwords don't match")

@app.route('/login')
def login():
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/check', methods = ['POST'])
def check():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_table = dynamodb.Table('users')
        response = user_table.scan(
            FilterExpression=Attr('username').eq(username) & Attr('password').eq(password)
        )

        if 'Items' in response and len(response['Items']) == 1:
            if 'password' in response['Items'][0]:
                if password == response['Items'][0]['password']:
                    session['username'] = username
                    return redirect('/')

    return render_template('login.html', error="Invalid username or password")

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
