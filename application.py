from flask import Flask, redirect, render_template, session, url_for, send_file, request, send_from_directory, abort
from pathlib import Path
import random
import string
import requests
import datetime
import os
import json

import cloudmersive_convert_api_client
from cloudmersive_convert_api_client.rest import ApiException

ROBOHASH_URL = "https://robohash.org/"
CLOUDMERSIVE_API_KEY = "d4b1a37f-5dd4-4283-8b70-5643606a1f2a"

application = Flask(__name__)
cm_cfg = cloudmersive_convert_api_client.Configuration()
cm_cfg.api_key['Apikey'] = CLOUDMERSIVE_API_KEY

@application.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('action1') == 'Generate':
            return render_main_page()
        else:
            pass  # unknown
    elif request.method == 'GET':
        return render_main_page()


@application.route("/cache/<string:ext>/<string:robohash>")
def cached_file(ext, robohash):
    if ext == "png":
        ensure_avatar_cached(robohash)
        return send_from_directory(application.root_path + '/cache/' + ext, robohash + "." + ext)
    if ext == "gif" or ext == "jpg" or ext == "pdf":
        return send_converted_avatar(ext, robohash)
    # Bad Request
    abort(400)


def send_converted_avatar(ext, robohash):
    converted_file_path = application.root_path + "/cache/" + ext
    converted_file_name = robohash + "." + ext
    if not is_cached(ext, robohash):
        ensure_avatar_cached(robohash)
        cm_instance = cloudmersive_convert_api_client.ConvertImageApi(cloudmersive_convert_api_client.ApiClient(cm_cfg))
        try:
            input_file = application.root_path + "/cache/png/" + robohash + ".png"
            # output_format = "JPEG/JPG" if ext == "jpg" else ext.upper()
            output_format = ext.upper()
            api_response = cm_instance.convert_image_image_format_convert("PNG", output_format, input_file)
            with open(converted_file_path + "/" + converted_file_name, 'wb') as f:
                # ugly workaround
                # see https://stackoverflow.com/questions/64938319/binary-data-gets-written-as-string-literal-how-to-convert-it-back-to-bytes)
                f.write(api_response[2:-1].encode('latin1').decode('unicode_escape').encode('latin1'))
                f.close()
        except ApiException as e:
            print("Exception when calling ConvertImageApi->convert_image_image_format_convert: %s\n" % e)
            abort(500)
    return send_from_directory(converted_file_path, converted_file_name)


def ensure_avatar_cached(robohash):
    if not is_cached("png", robohash):
        req = requests.get(ROBOHASH_URL + robohash + ".png")
        with open(application.root_path + "/cache/png/" + robohash + ".png", 'wb') as f:
            f.write(req.content)
            f.close()


def is_cached(ext, robohash):
    return Path(application.root_path + "/cache/" + ext + "/" + robohash + "." + ext).is_file()


def render_main_page():
    # generate random name
    apiResponse = requests.get('https://randomuser.me/api/')
    data = json.loads(apiResponse.content)
    name = data["results"][0]["name"]["first"]
    # generate robohash
    robohash = ''.join(random.choice(string.ascii_letters + string.digits) for a in range(16))
    # check local proxy cache first and download avatar if needed
    ensure_avatar_cached(robohash)
    # render main page, pointing to a locally cached avatar
    return render_template("avatar.html", robohash=robohash, year=datetime.date.today().year, robotName=name)


def init_cache():
    init_cache_subdirectory(application.root_path + "/cache/gif")
    init_cache_subdirectory(application.root_path + "/cache/jpg")
    init_cache_subdirectory(application.root_path + "/cache/pdf")
    init_cache_subdirectory(application.root_path + "/cache/png")


def init_cache_subdirectory(directory):
    if os.path.exists(directory):
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        os.makedirs(directory)


if __name__ == '__main__':
    init_cache()
    application.run(host="0.0.0.0", port=5001)
