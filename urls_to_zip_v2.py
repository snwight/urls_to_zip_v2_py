from flask import Flask
from flask import Response

import http.client as httplib
import urllib.parse as urlparse
import urllib.request

import json
import zipfile
import zipfile
import zipstream
import json
import tempfile

app = Flask(__name__)

DEFAULT_CONFIG_FILE_NAME = "./tiny_sample_archive.json"

@app.route('/images', methods=['GET'], endpoint='images')
def images():
    def iterable():
        with open(DEFAULT_CONFIG_FILE_NAME, 'r') as fp:
            config_obj = json.load(fp)
        # download and zip each image sequentially [sic] - yes should be on a thread
        for image_info in config_obj:
            with urllib.request.urlopen(image_info["url"]) as f:
                yield f.read()

    def generator():
        z = zipstream.ZipFile(mode='w', compression=zipfile.ZIP_DEFLATED)
        z.write_iter('iterable_chunks', iterable())
        for chunk in z:
            if chunk:
                yield chunk

    response = Response(generator(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format('files.zip')
    return response
