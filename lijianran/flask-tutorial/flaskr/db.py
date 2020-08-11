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


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""

    init_db()
    click.echo('初始化了数据库')


########################################################################


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


def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_lijing_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_lijing_db_command)


########################################################

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



# insert_table('person', '2023', ['person_id','person_name'], {'person_id':'1','person_name':'lijianran'})

def insert_table(table, year, insert_item, insert_dict):
    table_name = table+'_'+year

    item_data = []

    for item in insert_item:
        item_data.append('\''+insert_dict[item]+'\'')
    
    sql_insert = 'INSERT INTO '+table_name + '('+', '.join(insert_item)+') VALUES ('+', '.join(item_data)+')'

    db = get_lijing_db()
    db.execute(sql_insert)
    db.commit()


# update_table('person', year_select, item_person, update_dict, {'person_id': '='1''})
# update person_2020 set person_name = 'fsdfsldaj', gender = ? where person_id = ?'
def update_table(table, year, update_item, update_dict, condition_dict):
    table_name = table+'_'+year

    item_data = []
    for item in update_item:
        item_data.append(str(item)+' = \''+str(update_dict[item])+'\'')

    condition_data = []
    for item in condition_dict:
        condition_data.append(item + condition_dict[item])

    sql_update = 'UPDATE '+table_name+' SET '+', '.join(item_data)+' WHERE '+' AND '.join(condition_data)
    
    db = get_lijing_db()
    db.execute(sql_update)
    db.commit()


# select_table(['person', 'education', 'skill', 'workinfo'], '2023', {'person_id':'person', 'person_name':'person'}, {'gender':'男'})
# select_table('person', '2023', {'person_id':'person', 'person_name':'person'}, {'gender':'男'})
# select person_2023.person_id, person_2023.person_name from person_2023 where gender = '男'
# where gender = '男'
def select_table(table, year, select_item, condition_dict=None):
    if type(table) == str:
        #### 单表查询
        table_name = table+'_'+year

        select_string_list = []
        for item in select_item:
            select_table_name = select_item[item]+'_'+year
            select_string_list.append(select_table_name+'.'+item)

        select_string = ', '.join(select_string_list)

        if condition_dict != None:
            condition_data = []
            for item in condition_dict:
                condition_data.append(item + condition_dict[item])

            sql_select = 'SELECT '+select_string+' FROM ' + table_name+' WHERE '+' AND '.join(condition_data)
        else:
            sql_select = 'SELECT '+select_string+' FROM ' + table_name
        
        
        db = get_lijing_db()
        results = db.execute(sql_select).fetchall()

        result_list = []
        for result in results:
            result_dict = {}
            for item in select_item:
                result_dict[item] = result[item]

            result_list.append(result_dict)

        if len(result_list) == 1:
            return result_list[0]
        else:
            return result_list
    else:
        #### 多表查询
        select_string_list = []
        for item in select_item:
            select_table_name = select_item[item]+'_'+year
            select_string_list.append(select_table_name+'.'+item)

        select_string = ', '.join(select_string_list)

        sql_data = {}
        with open('flaskr\\lijing_table.json', 'r') as f:
            sql_data = json.load(f)

        # print(table)

        join_list = []
        for table_name in table:
            flag = False
            for item in sql_data[table_name]:
                
                if 'foreign_key' in item:
                    table1 = table_name+'_'+year
                    key1 = item['foreign_key'][0]
                    table2 = item['foreign_key'][1] + '_'+year
                    key2 = item['foreign_key'][2]
                    join_string = 'JOIN '+table1+' ON '+table1+'.'+key1+' = '+table2+'.'+key2

                    flag = True
                    join_list.append(join_string)
            
            if not flag:
                join_list.insert(0, table_name+'_'+year)

        if condition_dict != None:
            condition_data = []
            for item in condition_dict:
                condition_data.append(item + condition_dict[item])

            sql_select = 'SELECT '+select_string+' FROM ' + ' '.join(join_list)+' WHERE '+' AND '.join(condition_data)
        else:
            sql_select = 'SELECT '+select_string+' FROM ' + ' '.join(join_list)

        print(sql_select)
        db = get_lijing_db()
        results = db.execute(sql_select).fetchall()

        result_list = []
        for result in results:
            result_dict = {}
            for item in select_item:
                result_dict[item] = result[item]

            result_list.append(result_dict)

        if len(result_list) == 1:
            return result_list[0]
        else:
            return result_list




def get_item_list(table):
    item_list = []

    item_list_dict = {
        'person': ['person_name', 'gender', 'id_number', 'phone', 'political_status', 'time_Party', 'time_work', 'address', 'resume'],
        'education': ['edu_start', 'time_edu_start', 'school_edu_start', 'major_edu_start', 'edu_end', 'time_edu_end', 'school_edu_end', 'major_edu_end'],
        'skill': ['skill_title', 'time_skill', 'skill_unit', 'skill_number'],
        'workinfo': ['time_school', 'work_kind', 'job_post', 'time_retire']
    }
    if type(table) == list:
        for table_name in table:
            if table_name in item_list_dict:
                item_list = item_list + list(item_list_dict[table_name])
    elif type(table) == str:
        item_list = item_list_dict[table]
    else:
        pass

    return item_list



def float_int_string(float_num):
    if type(float_num) != str:
        float_num = str(int(float_num))
    return float_num