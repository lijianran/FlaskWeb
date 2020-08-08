import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

import os
import json

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')   #定义一个inti-db的命令行，就可以直接使用命令行，不用flask run
@with_appcontext
def init_db_command():    
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('初始化了数据库.')    #输出一个初始化成功



def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_lijing_db)
    app.cli.add_command(init_lijing_db_command)
    app.cli.add_command(init_db_command)


##########--------

def get_lijing_db():
    if 'lijing_db' not in g:
        g.lijing_db = sqlite3.connect(
            os.path.join(current_app.instance_path, 'lijing.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.lijing_db.row_factory = sqlite3.Row

    return g.lijing_db


def close_lijing_db(e=None):
    db = g.pop('lijing_db', None)

    if db is not None:
        db.close()


def init_lijing_db():
    db = get_lijing_db()

    with current_app.open_resource('lijing.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-lijing-db')
@with_appcontext
def init_lijing_db_command():
    init_lijing_db()
    click.echo('Initialized the lijing database.')



def create_table(table_list, year):
    for table in table_list:
        table_name = table+'_'+year
        
        sql_data = {}
        with open('flaskr\\lijing_table.json', 'r') as f:
            sql_data = json.load(f)

        item_list = []

        for item in sql_data[table]:
            for item_name in item:
                if item_name == 'foreign_key':
                    foreign_key_list = item['foreign_key']

                    item_list.append(
                        'FOREIGN KEY('+foreign_key_list[0]+') REFERENCES '+foreign_key_list[1]+'_'+year+'('+foreign_key_list[2]+')')

                elif item_name == 'primary_key':
                    item_list.append('PRIMARY KEY'+str(item[item_name]))
                else:
                    item_list.append(str(item_name)+' '+str(item[item_name]))
        
        
        item_string = ', '.join(item_list)

        sql_create = 'CREATE TABLE '+table_name+'('+item_string+')'
        
        db = get_lijing_db()
        db.execute(sql_create)
        db.commit()



