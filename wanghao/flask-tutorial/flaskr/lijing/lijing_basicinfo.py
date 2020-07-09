from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required

#from flaskr.db import get_db, get_lijing_db

#from flaskr.lijing.lijing_index import float_int_string

# from random import choice
# import os
# import xlrd
# import xlsxwriter
# import json
# import datetime
# from pypinyin import lazy_pinyin

bp = Blueprint('lijing_basicinfo', __name__, url_prefix='/lijing_basicinfo')


@bp.route('/hello')
@login_required
def hello():
    return render_template('lijing/basicInfo.html')