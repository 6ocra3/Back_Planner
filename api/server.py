import requests
import threading
import argparse

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DB.interaction.interaction import DbInteraction
from flask import Flask, request
from utils import config_parser

class Server:
    def __init__(self, host, port, db_host, db_port, db_user, db_password, db_name, rebuild_db=False):
        self.host = host
        self.port = port

        self.db = DbInteraction(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db_name=db_name,
        rebuild_db=rebuild_db
    )

        self.app = Flask(__name__)
        self.app.add_url_rule("/shutdown", view_func=self.shutdown)
        self.app.add_url_rule("/", view_func=self.get_home)
        self.app.add_url_rule("/home", view_func=self.get_home)

    def run_server(self):
        self.server = threading.Thread(target=self.app.run, kwargs={"host": self.host, "port": self.port})
        self.server.start()
        return self.server

    def shutdown_server(self):
        request.get(f'http://{self.host}:{self.port}/shutdown')

    def shutdown(self):
        terminate_func = request.environ.get("werkzeuq.server.shutdown")
        if terminate_func:
            terminate_func()

    def get_home(self):
        return "Hello world!"
    
    def add_user_info(self):
        request_body = dict()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, dest="config")

    args = parser.parse_args()
    config = config_parser(args.config)

    server_host = config["SERVER_HOST"]
    server_port = config["SERVER_PORT"]
    db_host = config["DB_HOST"]
    db_port=config["DB_PORT"]
    db_user=config["DB_USER"]
    db_password=config["DB_PASSWORD"]
    db_name=config["DB_NAME"]
    rebuild_db=config["REBUILD_DB"]
    
    server = Server(host=server_host, port=server_port, db_host=db_host, db_port=db_port, db_user=db_user, db_password=db_password, db_name=db_name, rebuild_db=rebuild_db)
    server.run_server()