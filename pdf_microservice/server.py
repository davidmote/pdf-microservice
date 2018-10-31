import io
import json
import logging
import os.path
import shutil
import tempfile
import zipfile

from flask import Flask, request, send_file, abort

from pydf import template_to_pdf, unzip, find_index


ALLOWED_EXTENSIONS = set(['zip', 'htm', 'html', 'css', 'png', 'jpg', 'jpeg', 'gif', 'json'])


app = Flask(__name__)


def get_from_files(request, name, required=True):
    """ Given a request and a file, return the given file for the request.
    If the file is missing and optional then return None instead, but raises
    if the file was required.
    """

    if name not in request.files and required:
        abort(400, f'{name} not in request body.')
    elif name not in request.files and not required:
        return None

    request_file = request.files[name]

    if not allowed_file(request_file.filename):
        raise abort(400, f'Provided value for {name} was an invalid file type.')

    return request_file


def allowed_file(filename):
    """ Checks if the specified filename is an allowed extension """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.before_first_request
def setup_logging():
    """ Enable logging behind a wsgi service such as gunicorn
    https://github.com/benoitc/gunicorn/issues/379
    """
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.route('/', methods=['GET'])
def check_online():
    """ Health check """
    return 'Online... waiting for requests.'


@app.route('/', methods=['POST'])
def generate_pdf():
    """ Accepts template file uploads and returns a PDF file attachment """

    bundle = get_from_files(request, 'template')  # HTML template and assets
    params = get_from_files(request, 'params', required=False)  # JSON paramters
    config = get_from_files(request, 'config', required=False)  # Weasyprint configuration

    if zipfile.is_zipfile(bundle):
        tmp_dir = tempfile.mkdtemp()
        bundle_files = list(unzip(bundle, tmp_dir))

        for name in bundle_files:
            if os.path.isfile(name) and not allowed_file(name):
                abort(400, f'zip file contains invalid file types: {name}')

        index_path = find_index(bundle_files)

        if not index_path:
            raise abort(400, description='unable to find index file')

        template = open(index_path)
    else:
        tmp_dir = None
        template = bundle

    pdf = io.BytesIO()

    template_to_pdf(
        template,
        pdf,
        json.load(params) if params else {},
        json.load(config) if config else {},
    )

    if tmp_dir:
        shutil.rmtree(tmp_dir)
        template.close()

    pdf.seek(0)

    return send_file(
        pdf,
        mimetype='application/pdf',
        attachment_filename='report.pdf',
        as_attachment=True
    )
