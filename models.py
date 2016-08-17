# coding: utf-8 
from peewee import *
from config import user, password, host

db = PostgresqlDatabase('kody', user=user, password=password, host=host)

class kodypocztowe(Model):
    gid = PrimaryKeyField()
    addr_postc = TextField()
    geom = TextField()
    region = IntegerField()

    class Meta:
        database = db 