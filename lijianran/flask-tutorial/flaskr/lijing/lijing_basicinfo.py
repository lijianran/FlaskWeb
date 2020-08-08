from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)

from flaskr.auth import login_required

from flaskr.db import get_db, get_lijing_db, create_table

import datetime

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

        session['year_current'] = year_list[0]

    return render_template('lijing/basicInfo.html',year_list=year_list, year_new=year_new)


@bp.route('/importData', methods=('GET', 'POST'))
def importData():
    if request.method == 'POST':
        db = get_lijing_db()

        year_select = request.form['year_select']
        
        year_data = db.execute('select year from year_list').fetchall()
        year_list = []
        for year in year_data:
            year_list.insert(0, year['year'])


        if year_select not in year_list:
            db.execute('insert into year_list (year, basicinfo, workinfo, honorinfo) values (?,?,?,?)', (year_select, 0, 0, 0, ))

            create_table(['person', 'education', 'workinfo', 'skill'], year_select)


        return redirect(url_for('lijing_basicinfo.hello'))