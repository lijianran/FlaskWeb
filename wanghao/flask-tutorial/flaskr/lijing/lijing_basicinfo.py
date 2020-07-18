from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

from flaskr.db import get_db, get_lijing_db

#from flaskr.lijing.lijing_index import float_int_string

# from random import choice
# import os
# import xlrd
# import xlsxwriter
import json
import datetime
# from pypinyin import lazy_pinyin

bp = Blueprint('lijing_basicinfo', __name__, url_prefix='/lijing_basicinfo')


@bp.route('/hello')
@login_required
def hello():
    db = get_lijing_db()

    year_data = db.execute('select year from year_list').fetchall()
    year_new = datetime.datetime.now().year
    year_list = []
    if len(year_data) == 0:
        year_list = ['暂无数据']
    else:
        for year in year_data:
            year_list.insert(0, year['year'])
        year_new = int(year_list[0]) + 1
        # if 'year_current' not in session:
        session['year_current'] = year_list[0]

    return render_template('lijing/basicInfo.html', year_list=year_list, year_new=year_new)



@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    db = get_lijing_db()

    data = []

    try:
        result = db.execute('select person_id, person_name, gender from person_' +
                            session['year_current']).fetchall()
        for row in result:
            d = {}
            d['id'] = row['person_id']
            d['name'] = row['person_name']
            d['gender'] = row['gender']
            data.append(d)
    except:
        return jsonify({'total': len(data), 'rows': data})

    if request.method == 'POST':
        print('post')
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        # print('get', limit)
        # print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
        # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
        # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了



@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':
        db = get_lijing_db()



        year_select = request.form.get('year_select')

        sql_data = {}
        with open('flaskr\sql_lijing.json', 'r') as f:
            sql_data = json.load(f)

        sql_create = ['', '', '', '']
        sql_create[0] = 'CREATE TABLE person_' + \
            year_select+sql_data['person']
        sql_create[1] = 'CREATE TABLE education_' + \
            year_select+sql_data['education']
        sql_create[2] = 'CREATE TABLE skill_' + \
            year_select+sql_data['skill']
        sql_create[3] = 'CREATE TABLE workinfo_' + \
            year_select+sql_data['workinfo']

        year_data = db.execute('select year from year_list').fetchall()
        year_list = []
        # year_new = datetime.datetime.now().year
        for year in year_data:
            year_list.insert(0, year['year'])

        if year_select not in year_list:
            db.execute('insert into year_list (year, basicinfo, workinfo, honorinfo) values (?,?,?,?)',
                       (year_select, 0, 0, 0, ))
            for sql in sql_create:
                db.execute(sql)
            db.commit()

        return redirect(url_for('lijing_basicinfo.hello'))
