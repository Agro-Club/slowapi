import logging

import pymongo
from fastapi import FastAPI
from mock import mock  # type: ignore
from starlette.applications import Starlette

from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

storage_uri = "mongodb://127.0.0.1:27017/"
async_storage_uri = "async+" + storage_uri


def clean_mongodb(uri):
    myclient = pymongo.MongoClient(uri)
    mydb = myclient["limits"]
    mycol = mydb["counters"]
    print(mycol)
    mycol.drop()


class TestSlowapi:
    def build_starlette_app(self, config={}, **limiter_args):
        limiter_args.setdefault("key_func", get_remote_address)
        limiter = Limiter(**limiter_args)
        app = Starlette(debug=True)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

        mock_handler = mock.Mock()
        mock_handler.level = logging.INFO
        limiter.logger.addHandler(mock_handler)
        return app, limiter

    def build_fastapi_mongo_app(self, config={}, **limiter_args):
        clean_mongodb(storage_uri)
        limiter_args.setdefault("key_func", get_remote_address)
        limiter = Limiter(storage_uri=async_storage_uri, **limiter_args)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        mock_handler = mock.Mock()
        mock_handler.level = logging.INFO
        limiter.logger.addHandler(mock_handler)
        return app, limiter

    def build_fastapi_app(self, config={}, **limiter_args):
        limiter_args.setdefault("key_func", get_remote_address)
        limiter = Limiter(**limiter_args)
        app = FastAPI()
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        mock_handler = mock.Mock()
        mock_handler.level = logging.INFO
        limiter.logger.addHandler(mock_handler)
        return app, limiter