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


