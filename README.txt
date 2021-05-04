-> Set up:

1. Create Lambda function with runtime "Python 3.8". As per the requirements, the configuration is 2048MB memory and 1 min timeout.
2. Download layer file from https://github.com/shelfio/libreoffice-lambda-layer/raw/master/layer.tar.br.zip and upload it to a bucket in S3.
3. In Lambda, go to Layers > Create layer. Choose "Upload a file from Amazon S3" and insert the S3 URL that points to the Layer file from step 2 (it's not possible to upload directly because the file is >50MB). In "Compatible runtimes" choose "Python 3.8".
4. After creating the Layer, add it to the Lambda function created in step 1 - it will be listed in the drop down after you choose "Custom Layers".
5. I included a test Lambda function ('test-lambda-docx-to-pdf.py'), which loads up a docx file from S3 and passes it to the parent Lambda function. Then, it synchronously gets the response from the parent Lambda with the converted file.

-> Notes:

1. I'm assuming that the event passed to the conversion Lambda contains the fields `file_name` and 'file_content'. 
	-> `file_name` is just a string with the original file name.
	-> `file_content` is an ASCII string containing the binary content of the doc file, encoded in base64.
2. The output of the lambda function also has the fields `file_name` and 'file_content', where:
	-> `file_name` is the original file name with the original extension replaced by '.pdf'
	-> `file_content` is an ASCII string containing the binary content of the pdf file, encoded in base64.