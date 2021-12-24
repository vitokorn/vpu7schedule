import os

import orjson
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

from sqlalchemy.sql import ClauseElement
import telebot
import urllib3
http = urllib3.PoolManager()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config[
    'SQLALCHEMY_DATABASE_URI'] = os.environ.get('db')
app.jinja_env.auto_reload = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uid = db.Column(db.String)
    name = db.Column(db.String)


class Lessons(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True, index=True)
    room = db.Column(db.String)
    subject = db.Column(db.String)
    teacher = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    group = db.Column(db.String)
    order = db.Column(db.String)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String)
    username = db.Column(db.String)
    tid = db.Column(db.Integer)
    language_code = db.Column(db.String)
    group = db.Column(
        db.Integer,
        db.ForeignKey("group.id", ondelete="CASCADE"),
        nullable=False
    )


class User:
    def __init__(self, name):
        self.name = name
        self.group = None


user_dict = {}


@bot.message_handler(commands=['start'])
def start(message):
    print(message.from_user)
    if message.from_user.language_code == "uk":
        bot.reply_to(message, 'Привiт, ' + message.from_user.first_name)
    elif message.from_user.language_code == "ru":
        bot.reply_to(message, 'Привет, ' + message.from_user.first_name)
    else:
        bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(commands=['set'])
def setgroup(message):
    if message.from_user.language_code == "uk":
        bot.reply_to(message, 'Напиши назву своєї групи')
    elif message.from_user.language_code == "ru":
        bot.reply_to(message, 'Напиши название своей группы')
    else:
        bot.reply_to(message, 'Write your group name')
    bot.register_next_step_handler(message, process_group_step)


# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)

def process_group_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        st = Student.query.filter_by(tid=message.from_user.id).first()
        if st is None:
            group = Group.query.filter_by(name=message.text).first()
            get_or_create(db.session,Student,tid=message.from_user.id,defaults={'language_code':message.from_user.language_code,'group':group.id})
        if message.from_user.language_code == "uk":
            bot.reply_to(message, 'Група обрана')
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, 'Группа выбрана')
        else:
            bot.reply_to(message, 'Group selected ')
        # bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


@app.route('/' + str(TOKEN), methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://vpu7shedule.herokuapp.com/' + TOKEN)
    return "!", 200


@app.route("/sync")
def sync():
    req = requests.get(url='http://schedule.in.ua:3200/groups', headers={'X-Institution': 'vische-profesiine-uchilische-7'})
    res = req.json()

    for r in res:
        group, create = get_or_create(db.session, Group, uid=r['_id'], name=r['name'])

    dt = datetime.today()
    monday = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
    sunday = (dt - timedelta(days=5)).strftime("%Y-%m-%d")

    groups = Group.query.filter_by()

    for g in groups:
        data = {
            'from': f'{monday}T10:00:00.000Z',
            'group': f'{g.uid}',
            'to': f'{sunday}T10:00:00.000Z'
        }
        nd = orjson.dumps(data)

        req3 = http.request(method='POST', url='http://schedule.in.ua:3200/lessons/query', body=nd,
                            headers={'X-Institution': 'vische-profesiine-uchilische-7'})
        res3 = orjson.loads(req3.data)
        for d in res3:
            lessons, create = get_or_create(db.session, Lessons, room=d['room']['name'], subject=d['subject']['name'],teacher=d['teacher']['name'],date=d['date'],group=d['group']['name'],order=d['order'])


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance, False
    else:
        params = {k: v for k, v in kwargs.items() if not isinstance(v, ClauseElement)}
        params.update(defaults or {})
        instance = model(**params)
        try:
            session.add(instance)
            session.commit()
        except Exception:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance, False
        else:
            return instance, True


@app.route('/')
def hello_world():
    return 'Hello World!'


