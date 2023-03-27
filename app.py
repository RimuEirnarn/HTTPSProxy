from flask import Flask, Response, abort, render_template, request, redirect
from future_router import Router
from urllib.parse import SplitResult, urlsplit
import requests
from requests import Response as OtherResponse
from http import HTTPStatus

app = Flask(__name__)
HTTPSTATUS = tuple(HTTPStatus)

route = Router()


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
    return new


@route.get("/")
def get_():
    data = fetch()
    if isinstance(data, Response):
        return data
    return form_response(requests.get(data))


@route.post("/")
def post_():
    data = fetch()
    if isinstance(data, Response):
        return data
    return form_response(requests.post(data, data=request.form))


route.init_app(app)

if __name__ == "__main__":
    app.run()
