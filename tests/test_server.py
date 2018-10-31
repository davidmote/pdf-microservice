from unittest import mock
import pytest


class Test_get_from_files(object):
    """ get_from_files() """

    def test_required_value_success(self):
        """ It should return the FileStorage from the input files """
        from pdf_microservice.server import get_from_files
        request = mock.Mock(files={})
        request.files['foo'] = mock.Mock(filename='data.json')
        result = get_from_files(request, 'foo', required=True)
        assert result == request.files['foo']

    def test_required_value_not_found(self):
        """ It should abort() when required input is not specified """
        from werkzeug.exceptions import HTTPException
        from pdf_microservice.server import get_from_files
        request = mock.Mock(files={})
        with pytest.raises(HTTPException) as excinfo:
            get_from_files(request, 'foo', required=True)
        assert excinfo.value.code == 400
        assert 'foo not in request body' in excinfo.value.description

    def test_not_required(self):
        """ It should return None if not specfied and not required """
        from pdf_microservice.server import get_from_files
        request = mock.Mock(files={})
        result = get_from_files(request, 'foo', required=False)
        assert result is None

    def test_invalid_file_type(self):
        """ It should abort() on invalid file type """
        from werkzeug.exceptions import HTTPException
        from pdf_microservice.server import get_from_files
        request = mock.Mock(files={})
        request.files['foo'] = mock.Mock(filename='data.xls')
        with pytest.raises(HTTPException) as excinfo:
            get_from_files(request, 'foo', required=True)
        assert excinfo.value.code == 400
        assert 'invalid file type' in excinfo.value.description


class Test_allowed_file:
    """ allowed_file() """

    @pytest.mark.parametrize('extension', [
        'zip', 'htm', 'html', 'css', 'png', 'jpg', 'jpeg', 'gif', 'json'])
    def test_sucess(self, extension):
        from pdf_microservice.server import allowed_file
        assert allowed_file(f'myfile.{extension}') is True

    def test_fail(self, tmpdir):
        from pdf_microservice.server import allowed_file
        assert allowed_file('report.junk') is False


class Test_check_online:
    """ check_online() """

    def test_http_success(self, app):
        response = app.get('/')
        assert response.status_code == 200


class Test_generate_pdf:
    """ generate_pdf() """

    def test_http_success_with_html(self, app):
        """ It should be able to process a standalone HTML template """
        import io
        response = app.post('/', data={
            'template': (io.BytesIO(b'<b>hello world</b>'), 'report.html')
        })
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

    def test_http_fail_with_invalid_zip_contents(self, tmpdir, app):
        """ It should fail if the zip bundle contains invalid files """
        import zipfile
        zip_file = tmpdir.join('bundle.zip')
        with zipfile.ZipFile(zip_file, 'w') as zip_fp:
            zip_fp.writestr('devious.exe', '1 / 0')

        with open(zip_file, 'rb') as fp:
            response = app.post('/', data={
                'template': (fp, 'report.zip')
            })
        assert response.status_code == 400
        assert b'contains invalid file types' in response.get_data()

    def test_http_fail_with_no_index(self, tmpdir, app):
        """ It should fail if the zip bundle does not have an index.html """
        import zipfile
        zip_file = tmpdir.join('bundle.zip')
        with zipfile.ZipFile(zip_file, 'w') as zip_fp:
            zip_fp.writestr('report.html', '<b>hello world</b>')

        with open(zip_file, 'rb') as fp:
            response = app.post('/', data={
                'template': (fp, 'report.zip')
            })
        assert response.status_code == 400
        assert b'unable to find index' in response.get_data()

    def test_http_success_ignore_hidden_files(self, tmpdir, app):
        """ It should ignore hidden files in bundle """
        import zipfile
        zip_file = tmpdir.join('bundle.zip')
        with zipfile.ZipFile(zip_file, 'w') as zip_fp:
            zip_fp.writestr('.DS_Store', '{}')
            zip_fp.writestr('main.css', 'body { font-family: sans; }')
            zip_fp.writestr('index.html', '<b>hello world</b>')

        with open(zip_file, 'rb') as fp:
            response = app.post('/', data={
                'template': (fp, 'report.zip')
            })
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

    def test_http_success_ignore_nested_directories(self, tmpdir, app):
        """ It should not validate directories """
        import zipfile
        zip_file = tmpdir.join('bundle.zip')
        with zipfile.ZipFile(zip_file, 'w') as zip_fp:
            zip_fp.writestr('.DS_Store', '{}')
            zip_fp.writestr('main.css', 'body { font-family: sans; }')
            zip_fp.writestr('index.html', '<b>hello world</b>')

        with open(zip_file, 'rb') as fp:
            response = app.post('/', data={
                'template': (fp, 'report.zip')
            })
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

    def test_http_success_with_zip(self, tmpdir, app):
        """ It should be able to process a template bundle ZIP """
        import zipfile
        zip_file = tmpdir.join('bundle.zip')
        with zipfile.ZipFile(zip_file, 'w') as zip_fp:
            zip_fp.writestr('assets/styles/main.css', 'body { font-family: sans; }')
            zip_fp.writestr('index.html', '<b>hello world</b>')

        with open(zip_file, 'rb') as fp:
            response = app.post('/', data={
                'template': (fp, 'report.zip')
            })
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
