import os
import traceback

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

first_start = "8:30"
first_end = "9:15"
second_start = "9:25"
second_end = "10:10"
third_start = "10:25"
third_end = "11:10"
fourth_start = "11:30"
fourth_end = "12:15"
fifth_start = "12:35"
fifth_end = "13:20"
sixth_start = "13:30"
sixth_end = "14:15"
seventh_start = "14:30"
seventh_end = "15:15"
eighth_start = "15:25"
eighth_end = "16:10"
ninth_start = "16:25"
ninth_end = "17:10"


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
    order = db.Column(db.Integer, nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String)
    username = db.Column(db.String)
    tid = db.Column(db.Integer)
    language_code = db.Column(db.String)
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("group.id", ondelete="CASCADE"),
        nullable=False
    )
    group = db.relationship("Group", backref="Student")


class User:
    def __init__(self, name):
        self.name = name
        self.group = None


user_dict = {}


def extract_arg(arg):
    return arg.split()[1:]


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


@bot.message_handler(commands=['today'])
def today(message):
    try:
        args = extract_arg(message.text)
        print(args)
        dt = datetime.now()
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)  # Returns a copy
        less = []
        if len(args) > 0:
            lessons = Lessons.query.filter_by(group=''.join(args), date=dt).order_by(Lessons.order)
        else:
            st = Student.query.filter_by(tid=message.from_user.id).first()
            lessons = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
        if lessons.first() is None:
            text = f'{dt.strftime("%d-%m-%Y")}\nПар нет'
            less.append(text)
        else:
            for le in lessons:
                start, end = None, None
                if le.order == 1:
                    start = first_start
                    end = first_end
                elif le.order == 2:
                    start = second_start
                    end = second_end
                elif le.order == 3:
                    start = third_start
                    end = third_end
                elif le.order == 4:
                    start = fourth_start
                    end = fourth_end
                elif le.order == 5:
                    start = fifth_start
                    end = fifth_end
                elif le.order == 6:
                    start = sixth_start
                    end = sixth_end
                elif le.order == 7:
                    start = seventh_start
                    end = seventh_end
                elif le.order == 8:
                    start = eighth_start
                    end = eighth_end
                elif le.order == 9:
                    start = ninth_start
                    end = ninth_end
                text = f'{le.order} Пара\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
                less.append(text)
        if message.from_user.language_code == "uk":
            bot.reply_to(message, '\n\n'.join(less))
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, '\n\n'.join(less))
        else:
            bot.reply_to(message, '\n\n'.join(less))
    except:
        print(traceback.format_exc())


@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    try:
        args = extract_arg(message.text)
        st = Student.query.filter_by(tid=message.from_user.id).first()
        dt = datetime.now() + timedelta(days=1)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)  # Returns a copy
        less = []
        if len(args) > 0:
            lessons = Lessons.query.filter_by(group=''.join(args), date=dt).order_by(Lessons.order)
        else:
            st = Student.query.filter_by(tid=message.from_user.id).first()
            lessons = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
        if lessons.first() is None:
            text = f'{dt.strftime("%d-%m-%Y")}\nПар нет'
            less.append(text)
        else:
            for le in lessons:
                start, end = None, None
                if le.order == 1:
                    start = first_start
                    end = first_end
                elif le.order == 2:
                    start = second_start
                    end = second_end
                elif le.order == 3:
                    start = third_start
                    end = third_end
                elif le.order == 4:
                    start = fourth_start
                    end = fourth_end
                elif le.order == 5:
                    start = fifth_start
                    end = fifth_end
                elif le.order == 6:
                    start = sixth_start
                    end = sixth_end
                elif le.order == 7:
                    start = seventh_start
                    end = seventh_end
                elif le.order == 8:
                    start = eighth_start
                    end = eighth_end
                elif le.order == 9:
                    start = ninth_start
                    end = ninth_end
                text = f'{le.order} Пара\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
                less.append(text)
        if message.from_user.language_code == "uk":
            bot.reply_to(message, '\n'.join(less))
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, '\n'.join(less))
        else:
            bot.reply_to(message, '\n'.join(less))
    except:
        print(traceback.format_exc())


@bot.message_handler(commands=['next_three_days'])
def next_three_days(message):
    try:
        args = extract_arg(message.text)
        st = Student.query.filter_by(tid=message.from_user.id).first()
        td = datetime.now()
        td = td.replace(hour=12, minute=0, second=0, microsecond=0)
        dt = datetime.now() + timedelta(days=1)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)
        tdat = datetime.now() + timedelta(days=2)
        tdat = tdat.replace(hour=12, minute=0, second=0, microsecond=0)

        less1 = []
        less2 = []
        less3 = []
        if len(args) > 0:
            lessons1 = Lessons.query.filter_by(group=''.join(args), date=td).order_by(Lessons.order)
            lessons2 = Lessons.query.filter_by(group=''.join(args), date=dt).order_by(Lessons.order)
            lessons3 = Lessons.query.filter_by(group=''.join(args), date=tdat).order_by(Lessons.order)
        else:
            st = Student.query.filter_by(tid=message.from_user.id).first()
            lessons1 = Lessons.query.filter_by(group=st.group.name, date=td).order_by(Lessons.order)
            lessons2 = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
            lessons3 = Lessons.query.filter_by(group=st.group.name, date=tdat).order_by(Lessons.order)
        if lessons1.first() is None:
            text = f'{td.strftime("%d-%m-%Y")}\nПар нет'
            less1.append(text)
        else:
            for le in lessons1:
                start, end = None, None
                if le.order == 1:
                    start = first_start
                    end = first_end
                elif le.order == 2:
                    start = second_start
                    end = second_end
                elif le.order == 3:
                    start = third_start
                    end = third_end
                elif le.order == 4:
                    start = fourth_start
                    end = fourth_end
                elif le.order == 5:
                    start = fifth_start
                    end = fifth_end
                elif le.order == 6:
                    start = sixth_start
                    end = sixth_end
                elif le.order == 7:
                    start = seventh_start
                    end = seventh_end
                elif le.order == 8:
                    start = eighth_start
                    end = eighth_end
                elif le.order == 9:
                    start = ninth_start
                    end = ninth_end
                text = f'{td.strftime("%d-%m-%Y")}\n{le.order} Пара\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
                less1.append(text)
        if lessons2.first() is None:
            text = f'{dt.strftime("%d-%m-%Y")}\nПар нет'
            less2.append(text)
        else:
            for le in lessons2:
                start, end = None, None
                if le.order == 1:
                    start = first_start
                    end = first_end
                elif le.order == 2:
                    start = second_start
                    end = second_end
                elif le.order == 3:
                    start = third_start
                    end = third_end
                elif le.order == 4:
                    start = fourth_start
                    end = fourth_end
                elif le.order == 5:
                    start = fifth_start
                    end = fifth_end
                elif le.order == 6:
                    start = sixth_start
                    end = sixth_end
                elif le.order == 7:
                    start = seventh_start
                    end = seventh_end
                elif le.order == 8:
                    start = eighth_start
                    end = eighth_end
                elif le.order == 9:
                    start = ninth_start
                    end = ninth_end
                text = f'{dt.strftime("%d-%m-%Y")}\n{le.order} Пара\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
                less2.append(text)
        if lessons3.first() is None:
            text = f'{tdat.strftime("%d-%m-%Y")}\nПар нет'
            less3.append(text)
        else:
            for le in lessons3:
                start, end = None, None
                if le.order == 1:
                    start = first_start
                    end = first_end
                elif le.order == 2:
                    start = second_start
                    end = second_end
                elif le.order == 3:
                    start = third_start
                    end = third_end
                elif le.order == 4:
                    start = fourth_start
                    end = fourth_end
                elif le.order == 5:
                    start = fifth_start
                    end = fifth_end
                elif le.order == 6:
                    start = sixth_start
                    end = sixth_end
                elif le.order == 7:
                    start = seventh_start
                    end = seventh_end
                elif le.order == 8:
                    start = eighth_start
                    end = eighth_end
                elif le.order == 9:
                    start = ninth_start
                    end = ninth_end
                text = f'{tdat.strftime("%d-%m-%Y")}\n{le.order} Пара\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
                less3.append(text)
        if message.from_user.language_code == "uk":
            # bot.reply_to(message, '\n'.join(less))
            bot.send_message(chat_id=message.chat.id,text='\n\n'.join(less1))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less2))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less3))
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,text='\n\n'.join(less1))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less2))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less3))
        else:
            bot.send_message(chat_id=message.chat.id,text='\n\n'.join(less1))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less2))
            bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less3))
    except:
        print(traceback.format_exc())


@bot.message_handler(commands=['calls'])
def calls(message):
    try:
        less = []
        for order in range(1, 10):
            start, end = None, None
            if order == 1:
                start = first_start
                end = first_end
            elif order == 2:
                start = second_start
                end = second_end
            elif order == 3:
                start = third_start
                end = third_end
            elif order == 4:
                start = fourth_start
                end = fourth_end
            elif order == 5:
                start = fifth_start
                end = fifth_end
            elif order == 6:
                start = sixth_start
                end = sixth_end
            elif order == 7:
                start = seventh_start
                end = seventh_end
            elif order == 8:
                start = eighth_start
                end = eighth_end
            elif order == 9:
                start = ninth_start
                end = ninth_end
            text = f'{order} Пара {start} {end}'
            less.append(text)
        if message.from_user.language_code == "uk":
            bot.reply_to(message, '\n'.join(less))
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, '\n'.join(less))
        else:
            bot.reply_to(message, '\n'.join(less))
    except:
        print(traceback.format_exc())


@bot.message_handler(commands=['help'])
def help(message):
    msg = f'Команды: /today, /tomorrow, /next_three_days, /week, /nextweek, предназначены для получения расписания на определенное к-во дней. Имеют две формы:\n 1. Исходная (/today) – предназначена для получения расписания пользователю, который был ранее зарегистрирован.\n2. Дополненная (/today О1-20) – предназначена для получения расписания для произвольной группы (не требует регистрацию).\nДля регистрации необходимо ввести команду /set и в следующем сообщении указать свою группу.\n'
    bot.send_message(message.chat.id, msg)

# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)


def process_group_step(message):
    try:
        st = Student.query.filter_by(tid=message.from_user.id).first()
        print(st)
        if st is None:
            group = Group.query.filter_by(name=message.text).first()
            get_or_create(db.session, Student, tid=message.from_user.id,
                          defaults={'first_name': message.from_user.first_name, 'username': message.from_user.username,
                                    'language_code': message.from_user.language_code, 'group': group})
        else:
            group = Group.query.filter_by(name=message.text).first()
            st.group = group.id
            st.first_name = message.from_user.first_name
            st.username = message.from_user.username
            db.session.commit()
        if message.from_user.language_code == "uk":
            bot.reply_to(message, 'Група обрана')
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, 'Группа выбрана')
        else:
            bot.reply_to(message, 'Group selected ')
        # bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        print(traceback.format_exc())
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
    req = requests.get(url='http://schedule.in.ua:3200/groups',
                       headers={'X-Institution': 'vische-profesiine-uchilische-7'})
    res = req.json()

    for r in res:
        group, create = get_or_create(db.session, Group, uid=r['_id'], name=r['name'])

    dt = datetime.today()
    mnd = dt - timedelta(days=dt.weekday())
    monday = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
    sunday = (mnd + timedelta(days=5)).strftime("%Y-%m-%d")

    groups = Group.query.filter_by()

    for g in groups:
        data = {
            'from': f'{monday}T10:00:00.000Z',
            'group': f'{g.uid}',
            'to': f'{sunday}T10:00:00.000Z'
        }
        print(f'497 {data}')
        nd = orjson.dumps(data)

        req3 = http.request(method='POST', url='http://schedule.in.ua:3200/lessons/query', body=nd,
                            headers={'X-Institution': 'vische-profesiine-uchilische-7'})
        res3 = orjson.loads(req3.data)
        print(f'504 {res3}')
        for d in res3:
            parseddate = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            print(f'506 {parseddate}')
            if d['room'] and d['room']['name']:
                room = d['room']['name']
            else:
                room = None
            if d['teacher'] and d['teacher']['name']:
                teacher = d['teacher']['name']
            else:
                teacher = None
            lessons, create = get_or_create(db.session, Lessons, room=room, subject=d['subject']['name'],
                                            teacher=teacher, date=parseddate, group=d['group']['name'],
                                            order=d['order'])
    result = {'sync': 'ok'}
    return result, 200


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
