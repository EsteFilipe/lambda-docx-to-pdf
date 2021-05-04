import os
import sys
import subprocess

# Install `brotli` package to /tmp/ and add to path (this is used for file
# extraction of LibreOffice)
subprocess.call(
    'pip install -Iv brotli==1.0.9 -t /tmp/ --no-cache-dir'.split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL)

sys.path.insert(1, '/tmp/')

import json
import boto3
import tarfile
import brotli
from io import BytesIO
import shutil
import base64

# Extract LibreOffice

buffer = BytesIO()
with open('/opt/lo.tar.br', mode='rb') as fout:
    file = fout.read()
    buffer.write(brotli.decompress(file))
    buffer.seek(0)
    with tarfile.open(fileobj=buffer) as tar:
        tar.extractall('/tmp')

"""
with tarfile.open('/opt/lo.tar.gz', "r:gz") as tar:
    tar.extractall('/tmp')
"""

os.environ['HOME'] = '/tmp'
WARM_UP_FILE_PATH = "/tmp/initfile.txt"

def lambda_handler(event, context):
    
    file_name = event['file_name']
    # Important: I'm assuming that the `file_content` field contains a string with 
    # a byte array encoded in base64. That's why I'm decoding it here
    file_content = base64.b64decode(event['file_content'])
    
    input_file_path = '/tmp/{}'.format(file_name)
    converted_file_name = os.path.splitext(file_name)[0] + '.pdf'
    converted_file_path = '/tmp/{}'.format(converted_file_name)
    
    # Container is not warm (fixes https://github.com/shelfio/libreoffice-lambda-layer/issues/20)
    if not os.path.exists(WARM_UP_FILE_PATH):
        with open(WARM_UP_FILE_PATH, 'w') as f:
            f.write('Warm up')
        convert_command = '/tmp/instdir/program/soffice.bin --headless --norestore --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --convert-to pdf:writer_pdf_Export --outdir /tmp {}'.format(WARM_UP_FILE_PATH).split();
        try:
            # Fails with code 81  
            subprocess.check_call(convert_command)
        except subprocess.CalledProcessError:
            print("Container is now warm.")

    # Save input file in memory
    with open(input_file_path, 'w+b') as f:
        binary_format = bytearray(file_content)
        f.write(binary_format)
    
    # Convert input file
    convert_command = '/tmp/instdir/program/soffice.bin --headless --norestore --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --convert-to pdf:writer_pdf_Export --outdir /tmp'.split();
    convert_command += [input_file_path] # case the file name has spaces
    return_code = subprocess.check_call(convert_command)
    
    # Delete file to avoid loading up container memory
    os.remove(input_file_path)
    
    # --> For test purposes: 
    # Use this if you want to put the converted file into your S3 bucket and inspect it
    #s3_client = boto3.client('s3')
    #s3_response = s3_client.upload_file(
    #    Filename = converted_file_path, 
    #    Bucket = 'lambda-docx-to-pdf',
    #    Key = 'output/{}'.format(converted_file_name))
    # <--
        
    with open(converted_file_path, 'rb') as f:
        # Just like the input file, the output file will be encoded in
        # base64
        converted_file = json.dumps(
            {'file_name': converted_file_name,
             'file_content': base64.b64encode(f.read()).decode('ascii')})
         
    # Delete converted file to avoid loading up container memory
    os.remove(converted_file_path)
    
    return converted_file