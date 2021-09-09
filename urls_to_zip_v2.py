# -*- coding: utf-8 -*-

from flask import Flask
from flask import Response

import http.client as httplib
import urllib.parse as urlparse
import urllib.request

import json 
import os
import tempfile
import zipfile

app = Flask(__name__)

DEFAULT_CONFIG_FILE = "./tiny_sample_archive.json"
DEFAULT_IMAGE_ARCHIVE = "./tiny_sample_archive.zip"

@app.route('/images', methods=['GET'], endpoint='images')
def images():
    with open(DEFAULT_CONFIG_FILE, 'r') as fp:
        config_obj = json.load(fp)

    def generator():
        # oh the horror... we compress into a temp file then read from that
        local_arc = tempfile.NamedTemporaryFile()
        zf = zipfile.ZipFile(local_arc, mode='w', compression=zipfile.ZIP_DEFLATED)
        local_arc_fpos = 0
    
        # download from url given in config directly to compressed tempfile
        for image_info in config_obj:
            print("{}\nbefore file write: {}".format(image_info["filename"], local_arc_fpos))
            with urllib.request.urlopen(image_info["url"]) as imgfp:
                zf.writestr(data=imgfp.read(), zinfo_or_arcname=image_info["filename"])

                # rewind arc file to last starting offset, read to current EOF
                new_arc_fpos = local_arc.tell()
                local_arc.seek(local_arc_fpos)
                local_arc_fpos = new_arc_fpos
                print("after file write: {}".format(local_arc_fpos))
                yield local_arc.read()

        zf.close()

        # rewind one last time and flush to listener
        print("after file close: {}".format(local_arc.tell()))
        local_arc.seek(local_arc_fpos)
        yield local_arc.read()

    response = Response(generator(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format('files.zip')
    return response
