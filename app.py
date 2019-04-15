# -*- coding:utf-8 -*-
from flask import Flask, flash, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_socketio import SocketIO
from threading import Lock
from forms import LoginForm, SendForm
from models import Admin, Received, Send, db
from xbees import XBEE_ADDR, device, xbee_send_message
import click



app = Flask(__name__)
app.config.from_pyfile('settings.py')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

db.init_app(app)
login_manager = LoginManager(app)
socketIO = SocketIO(app)

thread = None
thread_lock = Lock()

pi_received_data = []


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
    global pi_received_data
    while True:
        socketIO.sleep(1)
        if pi_received_data:
            while pi_received_data:
                data = {'name':pi_received_data[0][0],'body':pi_received_data[0][1],'time':pi_received_data[0][2]}
                socketIO.emit('server_response',
                              {'data': data}, namespace='/test')
                pi_received_data.pop(0)


@app.route('/')
@app.route('/hello/<name>')
def hello(name='admin'):
    return '<h1>Hello %s </h1>'%name


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        admin=Admin.query.first()
        if admin:
            if username==admin.username and admin.validate_password(password):
                login_user(admin)
                flash('Welcome', 'info')
                return redirect(url_for('login'))
            flash('Invalid username or password', 'warning')
        else:
            flash('No account', 'warning')
    return render_template('login.html', form=form)


@app.route('/data')
@login_required
def dataList():
    messages_send = Send.query.order_by(Send.timestamp.desc()).all()
    messages_received = Received.query.order_by(Received.timestamp.desc()).all()
    return render_template('list.html',messages_send=messages_send, messages_received=messages_received)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success','info')
    return redirect(url_for('login'))


def sendData(name, body):
    print(name, body)
    xbee_send_message(device, XBEE_ADDR[name], body)


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form=SendForm()
    if form.validate_on_submit():
        name=form.name.data
        body=form.body.data
        send=Send(name=name, body=body)
        db.session.add(send)
        db.session.commit()
        if name in XBEE_ADDR:
            sendData(name, body)
            flash('Name:%s   Message:%s     Send Success !' %(name,body))
        else:
            flash('No Such Node')

        # sendData(name,body)
        return redirect(url_for('index'))

    return render_template('index.html', form=form)


#从树莓派接收到数据
@app.route('/post_pi',methods=['POST'])
def get_data():
    global pi_data
    import time
    name = request.form['name']
    body = request.form['body']
    received=Received(name=name, body=body)

    time = time.strftime('%Y-%m-%d %H:%M:%S')
    pi_received_data.append((name, body, time))

    db.session.add(received)
    db.session.commit()
    return 'Data Received'


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
    click.echo('Initializing the database')
    db.create_all()

    admin=Admin.query.first()

    if admin is not None:
        click.echo('The administrator already exists, updating...')
        admin.username=username
        admin.set_password(password)
    else:
        admin=Admin()
        admin.username=username
        admin.set_password(password)
        db.session.add(admin)

    db.session.commit()
    click.echo('Done')


if __name__ == '__main__':
    socketIO.run(app, debug=True, host='0.0.0.0')
    # app.run(debug=True, host='0.0.0.0')
