# -*- coding:utf-8 -*-
from flask import Flask, flash, request, render_template, redirect, url_for, json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_socketio import SocketIO
from threading import Lock
from forms import LoginForm, SendForm, NodeDeleteForm
from models import Admin, db
from xbees import XBEE_ADDR, device, xbee_send_message, discover_devices, RECEIVED_DATA
import click
import time


app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db.init_app(app)
login_manager = LoginManager(app)
socketIO = SocketIO(app)

thread = None
thread_lock = Lock()

MY_DATA = {}

LOGIN_FLAG = 0


@login_manager.user_loader
def load_user(user_id):
    user = Admin.query.get(int(user_id))
    return user


@socketIO.on('connect', namespace='/test')
def test():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketIO.start_background_task(target=background_thread)


def background_thread():
    global RECEIVED_DATA
    while True:
        socketIO.sleep(1)
        if RECEIVED_DATA:
            while RECEIVED_DATA:
                data = {'name': RECEIVED_DATA[0][0], 'body': RECEIVED_DATA[0][1], 'time': RECEIVED_DATA[0][2]}
                socketIO.emit('server_response',
                              {'data': data}, namespace='/test')

                MY_DATA[RECEIVED_DATA[0][2]] = {'name': RECEIVED_DATA[0][0], 'body': RECEIVED_DATA[0][1]}
                RECEIVED_DATA.pop(0)


@app.route('/')
@app.route('/hello/<name>')
def hello(name='admin'):
    return '<h1>Hello %s </h1>' % name


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin)
                flash('Welcome', 'info')
                return redirect(url_for('login'))
            flash('Invalid username or password', 'warning')
        else:
            flash('No account', 'warning')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success','info')
    return redirect(url_for('login'))


@app.route('/data')
@login_required
def dataList():
    s = '<head><title>数据汇总</title></head><div align="center"><h1>DataList</h1>'
    t = time.strftime('%Y_%m_%d')
    with open('Received_' + t + '.txt', 'a+') as f:
        f.seek(0, 0)
        data = f.readlines()

    s += '<h2>Have Received %s Messages</h2>' % str(len(data))
    for i in data:
        j = i.split()
        s += '-------------------------'
        s += '<h4>* %s&nbsp&nbsp&nbsp&nbsp%s</h4>' % (j[2], j[-1])
        s += '<p>%s</p>'% (' '.join(j[4:-2]))
    s += '******************************************************************<br>'
    s += '******************************************************************'

    with open('Send_' + t + '.txt', 'a+') as f:
        f.seek(0, 0)
        data = f.readlines()

    s += '<h2>Have Send %s Messages</h2>' % str(len(data))
    for i in data:
        j = i.split()
        s += '-------------------------'
        s += '<h4>* %s&nbsp&nbsp&nbsp&nbsp%s</h4>' % (j[2], j[-1])
        s += '<p>%s</p>' % (' '.join(j[4:-2]))

    s += '</div>'
    return s


def sendData(name, body):
    xbee_send_message(device, XBEE_ADDR[name], body)


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = SendForm()
    if form.validate_on_submit():
        name = form.name.data
        body = form.body.data

        if name != 'node0' and name in XBEE_ADDR:
            sendData(name, body)
            t = time.localtime()
            t1 = time.strftime('%Y_%m_%d', t)
            t2 = time.strftime('%H:%M:%S', t)
            with open('Send_' + t1 + '.txt', 'a+') as f:
                f.write('Send to %s : %s  at %s\n' % (name, body, t2))
            flash('Send to %s : %s at %s Successfully !' % (name, body, t2))
        else:
            flash('Target Node Error')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)


@app.route('/discover')
@login_required
def discover():
    discover_devices(device)
    return redirect(url_for('devices'))


@app.route('/discover_init')
@login_required
def discover_init():
    XBEE_ADDR.clear()
    discover_devices(device)
    return redirect(url_for('devices'))


@app.route('/devices')
@login_required
def devices():
    s = '<head><title>Zigbee节点</title></head><div align="center"><h3>Zigbee节点</h3>'
    for i, j in XBEE_ADDR.items():
        s += '<p>'+i+' : '+j+'</p>'
    s += '</div>'
    return s


@app.route('/delete',methods=['GET','POST'])
@login_required
def delete():
    form = NodeDeleteForm()
    if form.node.data or form.mac_addr.data:
        if form.node.data:
            n = form.node.data
            if n in XBEE_ADDR.keys():
                for i in XBEE_ADDR.keys():
                    if i == n:
                        del XBEE_ADDR[i]
                        break
                flash('Delete %s Successfully'%n)
            else:
                flash('Target Node Error')

        else:
            n = form.mac_addr.data
            if n in XBEE_ADDR.values():
                for i, j in XBEE_ADDR.items():
                    if j == n:
                        del XBEE_ADDR[i]
                        break
                flash('Delete %s Successfully' % n)
            else:
                flash('Target Node Error')

        return redirect(url_for('delete'))

    return render_template('delete.html',form=form)


# 登陆 http://127.0.0.1:5000/api/login?username=admin&password=123
# 登陆成功 返回0
# 账号密码错误 返回1
# 数据库没有管理员账户 返回2
# 之后返回的status若值为10，则表示未登陆
@app.route('/api/login')
def api_login():
    global LOGIN_FLAG
    user = request.args.get('username', 'admin')
    pwd = request.args.get('password', '123456')
    admin = Admin.query.first()
    if admin:
        if user == admin.username and admin.validate_password(pwd):
            LOGIN_FLAG = 1
            return json.dumps({'status': 0})
        else:
            return json.dumps({'status': 1})
    else:
        return json.dumps({'status': 2})


@app.route('/api/logout')
def api_logout():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        LOGIN_FLAG = 0
        return json.dumps({'status': 0})
    else:
        return json.dumps({'status': 10})


# 发送数据 http://127.0.0.1:5000/api/index?name=node1&body=hello
# 发送成功返回 0
# 发送失败返回 1
@app.route('/api/index')
def api_index():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        name = request.args.get('name','')
        body = request.args.get('body', '')
        if name != 'node0' and name in XBEE_ADDR:
            sendData(name, body)
            t = time.localtime()
            t1 = time.strftime('%Y_%m_%d', t)
            t2 = time.strftime('%H:%M:%S', t)
            with open('Send_' + t1 + '.txt', 'a+') as f:
                f.write('Send to %s : %s  at %s\n' % (name, body, t2))
            return json.dumps({'status': 0, 'message': {'name': name, 'body': body}})

        return json.dumps({'status': 1})
    else:
        return json.dumps({'status': 10})


@app.route('/api/discover')
def api_discover():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        discover_devices(device)
        return json.dumps({'status': 0, 'devices': XBEE_ADDR})
    else:
        return json.dumps({'status': 10})


@app.route('/api/discover_init')
def api_discover_init():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        XBEE_ADDR.clear()
        discover_devices(device)
        return json.dumps({'status': 0, 'devices': XBEE_ADDR})
    else:
        return json.dumps({'status': 10})


@app.route('/api/devices')
def api_devices():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        return json.dumps({'status': 0, 'devices': XBEE_ADDR})
    else:
        return json.dumps({'status': 10})


@app.route('/api/delete')
def api_delete():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        node = request.args.get('node', '')
        if node in XBEE_ADDR:
            del XBEE_ADDR[node]
            return json.dumps({'status': 0, 'nodes': XBEE_ADDR})
        else:
            return json.dumps({'status': 1, 'nodes': XBEE_ADDR})
    else:
        return json.dumps({'status': 10})


@app.route('/api/my_data')
def api_my_data():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        if len(MY_DATA):
            data = MY_DATA.copy()
            MY_DATA.clear()
            return json.dumps({'status': 0, 'data': data})
        else:
            return json.dumps({'status': 1})
    else:
        return json.dumps({'status': 10})


@app.route('/api/received_data')
def api_received_data():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        data = {}
        with open('Received_' + time.strftime('%Y_%m_%d') + '.txt', 'a+') as f:
            f.seek(0, 0)
            d = f.readlines()

        for i in d:
            j = i.split()
            data[j[-1]] = {'name': j[2], 'body': ' '.join(j[4:-2])}

        return json.dumps({'num': len(d), 'status': 0, 'data': data})
    else:
        return json.dumps({'status': 10})


@app.route('/api/send_data')
def api_send_data():
    global LOGIN_FLAG
    if LOGIN_FLAG:
        data = {}
        with open('Send_' + time.strftime('%Y_%m_%d') + '.txt', 'a+') as f:
            f.seek(0, 0)
            d = f.readlines()

        for i in d:
            j = i.split()
            data[j[-1]] = {'name': j[2], 'body': ' '.join(j[4:-2])}

        return json.dumps({'num': len(d), 'status': 0, 'data': data})
    else:
        return json.dumps({'status': 10})


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        db.drop_all()
        click.echo('Drop tables.')
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login')
def init(username, password):
    click.echo('Initializing the administrator')
    db.create_all()

    admin = Admin.query.first()

    if admin is not None:
        click.echo('The administrator already exists, updating...')
        admin.username=username
        admin.set_password(password)
    else:
        admin = Admin()
        admin.username = username
        admin.set_password(password)
        db.session.add(admin)

    db.session.commit()
    click.echo('Done')


if __name__ == '__main__':
    socketIO.run(app, debug=True, host='0.0.0.0')

