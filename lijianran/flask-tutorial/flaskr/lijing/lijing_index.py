from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session, send_file, send_from_directory
)

from flaskr.auth import login_required

import os

bp = Blueprint('lijing', __name__, url_prefix='/lijing')


@bp.route('/')
def index():
    return render_template('lijing/login.html')


@bp.route('/board')
@login_required
def board():
    return render_template('lijing/board.html')


@bp.route('/download_excel_file/<string:excel_filename>')
def download_excel_file(excel_filename):
    """
    下载src_file目录下面的文件
    eg：下载当前目录下面的123.tar 文件，eg:http://localhost:5000/download?fileId=123.tar
    :return:
    """
    # file_name = request.args.get('fileId')
    file_path = os.path.join(os.path.dirname(
        __file__), '..\\static', 'downloads', excel_filename)
    print(file_path)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "The downloaded file does not exist"


@bp.route('/set_year')
def set_year():
    year = request.args.get('year')
    session['year_current'] = year
    return jsonify({'msg': 'success'})