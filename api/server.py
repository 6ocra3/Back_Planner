import json
import threading
import argparse

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DB.interaction.interaction import DbInteraction
from DB.Models.models import Tasks
from flask import Flask, request
from flask_cors import CORS
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
        if rebuild_db:
            self.db.create_week("2022-07-03")
            self.db.create_task(task="Hello world1", date="2022-07-03", column=1)
            self.db.create_task(task="Hello world2", date="2022-07-03", column=0)
            self.db.create_task(task="Hello world3", date="2022-07-03", column=0)

        self.app = Flask(__name__)
        CORS(self.app)
        self.app.add_url_rule("/shutdown", view_func=self.shutdown)
        self.app.add_url_rule("/", view_func=self.get_home)
        self.app.add_url_rule("/home", view_func=self.get_home)
        self.app.add_url_rule("/create_task", view_func=self.create_task, methods=["POST"] )
        self.app.add_url_rule("/create_week", view_func=self.create_week, methods=["POST"] )
        self.app.add_url_rule("/edit_task", view_func=self.edit_task, methods=["PUT"] )
        self.app.add_url_rule("/edit_week", view_func=self.edit_week, methods=["PUT"] )
        self.app.add_url_rule("/get_week_tasks/<date>", view_func=self.get_task_for_week)
        self.app.add_url_rule("/get_task/<task_id>", view_func=self.get_task)
        self.app.add_url_rule("/get_week/<date>", view_func=self.get_week)
        self.app.add_url_rule("/edit_task_status", view_func=self.edit_task_status, methods=["PUT"])
        self.app.add_url_rule("/edit_task_day", view_func=self.edit_task_day, methods=["PUT"])

    def edit_task_status(self):
        request_body = dict(request.json)
        task_id = request_body["task_id"]
        status = request_body["status"]
        res = self.db.edit_task(task_id=task_id, status=status)
        if res:
            return "Succes", 200
        
    def edit_task_day(self):
        request_body = dict(request.json)
        task_id = request_body["task_id"]
        day = request_body["day"]
        value = request_body["value"]
        task = self.db.mysql_connection.session.query(Tasks).filter_by(id=task_id).first()
        new_days = task.days[:]
        new_days[day] = value
        res = self.db.edit_task(task_id=task_id, days=new_days)
        if res:
            return "Succes", 200

    def get_task(self, task_id):
        task = self.db.get_task(task_id=task_id)
        return task, 200

    def get_week(self, date):
        week = self.db.get_week(date=date)
        return week

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
    
    def create_task(self):
        request_body = dict(request.json)
        task = request_body["task"]
        date = request_body["date"]
        column = request_body["column"]
        newTask = self.db.create_task(task=task, date=date, column=column)
        return {"id": newTask["id"]}, 201
    
    def create_week(self):
        request_body = dict(request.json)
        date = request_body["date"]
        self.db.create_week(date=date)
        return f"Succes add week with date {date}", 201
    
    def edit_task(self):
        request_body = dict(request.json)
        rkeys = list(request_body.keys())
        task_text, status, days, description = None, None, None, None
        if "task_id" in rkeys:
            task_id = request_body["task_id"]
        if "task_text" in rkeys:
            task_text = request_body["task_text"]
        if "status" in rkeys:
            status = request_body["status"]
        if "days" in rkeys:
            days = request_body["days"]
        if "description" in rkeys:
            description = request_body["description"]
        res = self.db.edit_task(task_id=task_id, task_text=task_text, status=status, days=days, description=description)
        if res:
            return f"Succes edit {task_id}", 202
    
    def edit_week(self):
        request_body = dict(request.json)
        rkeys = list(request_body.keys())
        date = request_body["date"]
        tracker_order, list_order = None, None
        if "tracker_order" in rkeys:
            tracker_order = request_body["tracker_order"]
        if "list_order" in rkeys:
            list_order = request_body["list_order"]
        res = self.db.edit_week(date=date, tracker_order=tracker_order, list_order=list_order)
        if res:
            return f"Succes edit week {date}", 202
    
        
    def get_task_for_week(self, date):
        week = self.db.get_week(date=date)
        if not(week):
            self.db.create_week(date=date)
        tasks = self.db.filter_task_for_week_id(date=date)
        ans = dict()
        for i in tasks:
            temp = { "task":i.task, 
                     "status":i.status,
                     "days": i.days,
                     "description": i.description}
            ans[i.id] = temp
        ans = json.dumps(ans)
        return ans, 200


    
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
    rebuild_db = config["REBUILD_DB"] == "True"
    server = Server(host=server_host, port=server_port, db_host=db_host, db_port=db_port, db_user=db_user, db_password=db_password, db_name=db_name, rebuild_db=rebuild_db)

    server.run_server()