# coding: utf-8 
from flask import Flask, session, render_template, request, redirect, jsonify
import urllib
from config import keySecret
from db import *
from models import *

#app start
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/<code>')
def index(code):
    try:
        tempKod = kodypocztowe.select().where(kodypocztowe.addr_postc == '%s' % code).first()
        temp = tempKod.addr_postc
        geometry = db.execute_sql("""SELECT ST_AsGeoJSON(geom) FROM kodypocztowe WHERE addr_postc = '%s';""" % code)
        the_geom = geometry.fetchone()
        return the_geom
    except:
        return jsonify(code)

if __name__ == '__main__':
    app.secret_key = keySecret
    app.run(debug = True)