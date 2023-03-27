from flask import Flask, Response, abort, render_template, request, redirect
from urllib.parse import SplitResult, urlsplit
import requests
from requests import Response as OtherResponse
from http import HTTPStatus
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={'/': {'origins': '*'}})
HTTPSTATUS = tuple(HTTPStatus)
route = app

app.config['CORS_HEADERS'] = 'Content-Type'


def aborted(code: int, url: str):
    """Custom aborter"""
    status = HTTPSTATUS[HTTPSTATUS.index(code)]
    desc = status.description
    name = status.name
    if url == "":
        url = "#"
    response = Response(render_template(
        "error.html", error_code=code, name=name, desc=desc, url=url))
    response.status_code = code
    return abort(response)


def transorm_or_redirect(url: str):
    url_data: SplitResult = urlsplit(url)
    if not url_data.scheme in ("http", "https"):
        return aborted(400, url)
    if url_data.scheme == "http":
        return url
    return redirect(url)


def fetch():
    url = request.args.get("url", None)
    if url is None:
        return aborted(400, "#NULL")
    data = transorm_or_redirect(url)
    return data


def form_response(data: OtherResponse):
    new = Response(data.content)
    new.status_code = data.status_code
    new.content_type = data.headers['Content-Type']
    return new


@route.get("/")
@cross_origin(origin='*', headers=['Content-Type'])
def get_():
    data = fetch()
    if isinstance(data, Response):
        return data
    return form_response(requests.get(data))


@route.post("/")
@cross_origin(origin='*', headers=['Content-Type'])
def post_():
    data = fetch()
    if isinstance(data, Response):
        return data
    return form_response(requests.post(data, data=request.form))


if __name__ == "__main__":
    app.run()
