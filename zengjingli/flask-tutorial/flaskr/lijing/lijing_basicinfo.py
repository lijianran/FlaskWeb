from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)

from werkzeug.utils import secure_filename

from flaskr.auth import login_required

from flaskr.db import get_db, get_lijing_db,create_table,insert_table,select_table,get_item_list,float_int_string,update_table

import datetime

import xlrd
import xlsxwriter
import os
from pypinyin import lazy_pinyin

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


@bp.route('/jsondata', methods=('GET', 'POST'))
def jsondata():

    data = []

    try:

        result = select_table('person', session['year_current'],
                              {'person_id': 'person', 'person_name': 'person', 'gender': 'person'})
        for row in result:
            d = {}
            d['person_id'] = row['person_id']
            d['person_name'] = row['person_name']
            d['gender'] = row['gender']
            data.append(d)
    except:
        return jsonify({'total': len(data), 'rows': data})

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
        # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
        # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了



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


        f = request.files['file']
        filename = secure_filename(''.join(lazy_pinyin(f.filename)))

        if filename.endswith('.xlsx'):

            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, '..\\static\\uploads', filename)

            f.save(upload_path)

            data = xlrd.open_workbook(upload_path)
            table = data.sheet_by_index(0)
            print("总行数：" + str(table.nrows))
            print("总列数：" + str(table.ncols))

               # 找到标题
            dict_title = {
                '姓名': 'person_name', '性别': 'gender', '身份证号': 'id_number', '联系电话': 'phone', '政治面貌': 'political_status', '入党时间': 'time_Party', '参加工作时间': 'time_work', '家庭住址': 'address', '工作简历': 'resume',
                '第一学历': 'edu_start', '第一学历毕业时间': 'time_edu_start', '第一学历毕业学校': 'school_edu_start', '第一学历专业': 'major_edu_start', '最高学历': 'edu_end', '最高学历毕业时间': 'time_edu_end', '最高学历毕业学校': 'school_edu_end', '最高学历专业': 'major_edu_end',
                '专业技术职称': 'skill_title', '取得时间': 'time_skill', '发证单位': 'skill_unit', '发证文件批号': 'skill_number',
                '调入大集中学时间': 'time_school', '用工性质': 'work_kind', '工作岗位': 'job_post', '退休时间': 'time_retire'
            }

            row_title = table.row_values(0)
            print(row_title)

            title_id = {} # {'person_name':'1','gender':'2'}
            for i in dict_title:
                title_id[dict_title[i]] = -1
            print(title_id)

            for i in range(0, len(row_title)):
                title_name = row_title[i]
                if title_name in dict_title:
                    title_id[dict_title[title_name]] = i
            print(title_id)

            # 导入数据
            item = get_item_list(['person', 'education', 'skill', 'workinfo'])
            for i in range(1, table.nrows):
                row_value = table.row_values(i)

                insert_dict = {}
                for j in item:
                    if title_id[j] == -1:
                        insert_dict[j] = '暂无'
                    else:
                        insert_dict[j] = float_int_string(row_value[title_id[j]])
                        if len(insert_dict[j]) == 0:
                            insert_dict[j] = '暂无'
                
                item_person = get_item_list('person')
                insert_table('person', year_select, item_person, insert_dict)

                person_id = select_table('person', year_select, {'person_id': 'person'}, {'person_name': ' = \''+insert_dict['person_name']+'\''})['person_id']
                insert_dict['person_id'] = float_int_string(person_id)

                item_education = get_item_list('education')
                item_education.append('person_id')
                insert_table('education', year_select, item_education, insert_dict)

                item_skill = get_item_list('skill')
                item_skill.append('person_id')
                insert_table('skill', year_select, item_skill, insert_dict)

                item_workinfo = get_item_list('workinfo')
                item_workinfo.append('person_id')
                insert_table('workinfo', year_select, item_workinfo, insert_dict)

            os.remove(upload_path)

            return redirect(url_for('lijing_basicinfo.hello'))

            
        else:
            error = '请导入xlsx格式的文件'
            flash(error)
            return redirect(url_for('lijing_basicinfo.hello'))


@bp.route('/add_data', methods=('GET', 'POST'))
def add_data():
    insert_dict = {}

    item = get_item_list(['person', 'education', 'skill', 'workinfo'])  #返回的是所有25个字段

    year_select = session['year_current']   #当前年份

    for i in item:        #就是一个一个增加，如果没有增加，就先设置成暂无
        insert_dict[i] = request.args.get(i, '暂无', type=str)
        if insert_dict[i] == '':
            insert_dict[i] = '暂无'

    item_person = get_item_list('person')        
    insert_table('person', year_select, item_person, insert_dict)

    person_id = select_table('person', year_select, {'person_id': 'person'}, {'person_name': insert_dict['person_name']})['person_id']
    insert_dict['person_id'] = float_int_string(person_id)

    item_education = get_item_list('education')
    item_education.append('person_id')
    insert_table('education', year_select, item_education, insert_dict)

    item_skill = get_item_list('skill')
    item_skill.append('person_id')
    insert_table('skill', year_select, item_skill, insert_dict)

    item_workinfo = get_item_list('workinfo')
    item_workinfo.append('person_id')
    insert_table('workinfo', year_select, item_workinfo, insert_dict)

    msg = '成功添加教师' + insert_dict['person_name'] + '的信息'
    return jsonify({'msg': msg})



@bp.route('/search', methods=('GET', 'POST'))
def search():
    person_id = request.args.get('id', 0, type=int)
    year = session['year_current']

    item = {}
    table = ['person', 'education', 'skill', 'workinfo']
    for table_name in table:
        item_list = get_item_list(table_name)
        for i in item_list:
            item[i] = table_name

    condition = 'person_' + year + '.person_id'
    result = select_table(table, year, item, {condition: '=\''+float_int_string(person_id)+'\''})

    return jsonify(result)

@bp.route('/update_data', methods=('GET', 'POST'))
def update_data():
    year_select = session['year_current']

    update_dict = {}
    item = get_item_list(['person', 'education', 'skill', 'workinfo'])
    for i in item:
        update_dict[i] = request.args.get(i, '暂无', type=str)
        if update_dict[i] == '':
            update_dict[i] = '暂无'

    person_id = request.args.get('person_id', '0', type=str)
    condition_dict = {'person_id': ' = \''+person_id+'\''}


    item_person = get_item_list('person')
    update_table('person', year_select, item_person, update_dict, condition_dict)

    item_education = get_item_list('education')
    update_table('education', year_select, item_education, update_dict, condition_dict)

    item_skill = get_item_list('skill')
    update_table('skill', year_select, item_skill, update_dict, condition_dict)

    item_workinfo = get_item_list('workinfo')
    update_table('workinfo', year_select, item_workinfo, update_dict, condition_dict)


    msg = '成功修改教师' + update_dict['person_name'] + '的信息'
    return jsonify({'msg': msg})


@bp.route('/search_data', methods=('GET', 'POST'))
def search_data():
    #获取搜索选的字段，然后获取查询的某个字
    search_item = request.args.get('search_item','暂无',type=str)
    search_string = request.args.get('search_string','暂无',type=str)

    year = session['year_current']

    result = select_table(['person','education','skill','workinfo'],year,{'person_id':'person','person_name':'person','gender':'person'},
    {search_item: ' like \'%'+search_string+'%\''})

    data = []
    if type(result) == dict:
        data.append(result)
    else:
        data = result

    msg = '成功查询到'+str(len(data))+'条信息'
    return jsonify({'msg': msg, 'total': len(data), 'rows': data})


@bp.route('/exportData', methods=('GET', 'POST'))
def exportData():

    export_item = {}
    table = ['person', 'education', 'skill', 'workinfo']
    item = get_item_list(table)

    for table_name in table:
        item_table = get_item_list(table_name)
        for i in item_table:
            if request.args.get(i) == 'true':
                export_item[i] = table_name


    year = session['year_current']
    flag_search = request.args.get('flag_search')

    id_list = []
    if flag_search == 'true':
        id_list = request.args.getlist("id_list[]")
    else:
        person_data = select_table('person', year, {'person_id': 'person'})
        for i in person_data:
            id_list.append(str(i['person_id']))

    table_data = []
    for i in id_list:
        result = select_table(table, year, export_item, {'person_'+year+'.person_id': ' = \''+i+'\''})
        table_data.append(result)

    item_name_dict = {
        'person_name': '姓名', "gender": '性别', "id_number": '身份证号', "phone": '联系电话', "political_status": '政治面貌', "time_Party": '入党时间', "time_work": '参加工作时间', "address": '家庭住址', "resume": '个人简历',
        "edu_start": '第一学历', "time_edu_start": '第一学历毕业时间', "school_edu_start": '第一学历毕业学校', "major_edu_start": '第一学历专业', "edu_end": '最高学历', "time_edu_end": '最高学历毕业时间', "school_edu_end": '最高学历毕业学校', "major_edu_end": '最高学历专业',
        "skill_title": '专业技术职称', "time_skill": '职称取得时间', "skill_unit": '职称发证单位', "skill_number": '发证文件批号',
        "time_school": '调入大集中学时间', "work_kind": '用工性质', "job_post": '工作岗位', "time_retire": '退休时间'
    }

    workbook = xlsxwriter.Workbook('flaskr\\static\\downloads\\exportData.xlsx')
    worksheet = workbook.add_worksheet('Sheet1')
    col = 0
    for i in export_item:
        worksheet.write(0, col, item_name_dict[i])
        col = col+1
    for i in range(len(id_list)):
        col = 0
        print(i)
        for j in export_item:
            worksheet.write(i+1, col, table_data[i][j])
            col = col+1
            print(j)

    workbook.close()
    # # print(os.path.join(os.path.dirname(
    # #     __file__), 'static', 'downloads', 'exportData.xlsx'))
    msg = '成功导出'+str(len(id_list))+'条信息'

    return jsonify({'msg': msg, 'filename': 'exportData.xlsx'})



