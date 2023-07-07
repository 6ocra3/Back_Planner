import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client.client import MySQLConnection
from Models.models import Base, User, Weeks
from exceptions import UserNotFoundException






class DbInteraction:
    def __init__(self, host, port, user, password, db_name, rebuild_db=False):
        self.mysql_connection = MySQLConnection(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
            rebuild_db=rebuild_db,
        )
        self.engine = self.mysql_connection.connection.engine

        if rebuild_db:            
            self.create_table_weeks()
            self.create_table_tasks()

    def create_table_tasks(self):
        if not self.engine.dialect.has_table(self.engine, "tasks"):
            Base.metadata.tables["tasks"].create(self.engine)
        else:
            self.mysql_connection.execute_query("DROP TABLE IF EXISTS tasks")
            Base.metadata.tables["tasks"].create(self.engine)
    
    def create_table_weeks(self):
        if not self.engine.dialect.has_table(self.engine, "weeks"):
            Base.metadata.tables["weeks"].create(self.engine)
        else:
            self.mysql_connection.execute_query("DROP TABLE IF EXISTS weeks")
            Base.metadata.tables["weeks"].create(self.engine)

    def create_week(self, date):
        week = Weeks(
            date = date,
            tracker_order = [],
            list_order = []
        )
        self.mysql_connection.session.add(week)
        return self.get_week(date)
    
    def get_week(self, date):
        week = self.mysql_connection.session.query(Weeks).filter_by(date=date).first()
        if week:
            self.mysql_connection.session.expire_all()
            return {"date": week.date, "tracker_order": week.tracker_order, "list_order": week.list_order}
        else:
            raise UserNotFoundException("Week not found")


if __name__ == "__main__":
    db = DbInteraction(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="pass",
        db_name="planner_db",
        rebuild_db=True
    )
    print(db.create_week("2021-08-16"))