import os
import traceback

import flask
import orjson
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

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
host = os.environ.get('host')
WEBHOOK_SSL_CERT = './webhook_cert.pem'

ua_time = timezone('Europe/Kiev')

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
    cid = db.Column(db.Integer)
    notification_time = db.Column(db.Time, default=datetime.utcnow)


class User:
    def __init__(self, name):
        self.name = name
        self.group = None


user_dict = {}


def aggregatio(lessons,less,dt):
    date = f'{dt.strftime("%d.%m.%Y")}\n'
    less.append(date)
    ignore_order = 0
    for le in lessons:
        if ignore_order == le.order:
            less[-1] += f'\n2 группа:\n{le.room}\n{le.teacher}'
        else:
            if lessons.filter_by(order=le.order).count() > 1:
                ignore_order = le.order
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
            if le.teacher:
                text = f'⏰{le.order} Урок\n{start} {end}\n{le.subject}\n{le.room}\n{le.teacher}'
            else:
                text = f'⏰{le.order} Урок\n{start} {end}\n{le.subject}\n{le.room}'
            less.append(text)
    return less


def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=['start'])
def start(message):
    print(message.from_user)
    st = Student.query.filter_by(tid=message.from_user.id).first()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if st is None:
        text = ""
        if message.from_user.language_code == "uk":
            item1 = telebot.types.KeyboardButton("Вибрати групу")
            item2 = telebot.types.KeyboardButton("Як користуватися ботом")
            markup.add(item1,item2)
            text = 'Привiт, '
        elif message.from_user.language_code == "ru":
            item1 = telebot.types.KeyboardButton("Выбрать группу")
            item2 = telebot.types.KeyboardButton("Как пользоваться ботом")
            markup.add(item1,item2)
            text = 'Привет, '
        else:
            item1 = telebot.types.KeyboardButton("Set group")
            item2 = telebot.types.KeyboardButton("How to use a bot")
            markup.add(item1,item2)
            text = 'Hello, '
        text += message.from_user.first_name
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)
    else:
        if message.from_user.language_code == "uk":
            item1 = telebot.types.KeyboardButton("Розклад на сьогодні")
            item2 = telebot.types.KeyboardButton("Розклад на завтра")
            item3 = telebot.types.KeyboardButton("Розклад на три дні")
            item4 = telebot.types.KeyboardButton("Розклад на тиждень")
            item5 = telebot.types.KeyboardButton("Розклад дзвінків")
            item6 = telebot.types.KeyboardButton("Змінити групу")
            item7 = telebot.types.KeyboardButton("Моя група")
            item8 = telebot.types.KeyboardButton("Як користуватися ботом")
            item9 = telebot.types.KeyboardButton("Змiнити час отримання розкладу")
            markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9)
            bot.send_message(chat_id=message.chat.id, text='Привiт, ' + message.from_user.first_name,reply_markup=markup)
        elif message.from_user.language_code == "ru":
            item1 = telebot.types.KeyboardButton("Расписание на сегодня")
            item2 = telebot.types.KeyboardButton("Расписание на завтра")
            item3 = telebot.types.KeyboardButton("Расписание на три дня")
            item4 = telebot.types.KeyboardButton("Расписание на неделю")
            item5 = telebot.types.KeyboardButton("Расписание звонков")
            item6 = telebot.types.KeyboardButton("Сменить группу")
            item7 = telebot.types.KeyboardButton("Моя группа")
            item8 = telebot.types.KeyboardButton("Как пользоваться ботом")
            item9 = telebot.types.KeyboardButton("Изменить время получения расписания")
            markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9)
            bot.send_message(chat_id=message.chat.id, text='Привет, ' + message.from_user.first_name,reply_markup=markup)
        else:
            item1 = telebot.types.KeyboardButton("Schedule for today")
            item2 = telebot.types.KeyboardButton("Schedule for tomorrow")
            item3 = telebot.types.KeyboardButton("Schedule for three days")
            item4 = telebot.types.KeyboardButton("Week schedule")
            item5 = telebot.types.KeyboardButton("Call Schedule")
            item6 = telebot.types.KeyboardButton("Change group")
            item7 = telebot.types.KeyboardButton("My group")
            item8 = telebot.types.KeyboardButton("How to use a bot")
            item9 = telebot.types.KeyboardButton("Change schedule notification")
            markup.add(item1,item2,item3,item4,item5,item6,item7,item8,item9)
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


@bot.message_handler(commands=['group'])
def group(message):
    st = Student.query.filter_by(tid=message.from_user.id).first()
    if message.from_user.language_code == "uk":
        bot.reply_to(message, f'Твоя група {st.group.name}')
    elif message.from_user.language_code == "ru":
        bot.reply_to(message, f'Твоя группа {st.group.name}')
    else:
        bot.reply_to(message, f'Your group {st.group.name}')


@bot.message_handler(commands=['today'])
def today(message):
    try:
        if message.text.startswith("Розклад на сьогодні") or message.text.startswith("Расписание на сегодня") or message.text.startswith("Schedule for today"):
            if message.from_user.language_code == "uk":
                try:
                    args = message.text.split('Розклад на сьогодні ')[1]
                except:
                    args = ""
                print(args)
            elif message.from_user.language_code == "ru":
                try:
                    args = message.text.split('Расписание на сегодня ')[1]
                except:
                    args = ""
                print(args)
            else:
                try:
                    args = message.text.split('Schedule for today ')[1]
                except:
                    args = ""
                print(args)
        else:
            args = extract_arg(message.text)
        print(args)
        dt = datetime.now(ua_time)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0,tzinfo=None)  # Returns a copy
        less = []
        if len(args) > 0:
            lessons = Lessons.query.filter_by(group=''.join(args), date=dt).order_by(Lessons.order)
        else:
            st = Student.query.filter_by(tid=message.from_user.id).first()
            lessons = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
        if lessons.first() is None:
            text = f'{dt.strftime("%d.%m.%Y")}\nПар нет'
            less.append(text)
        else:
            less = aggregatio(lessons, less, dt)
        if message.from_user.language_code == "uk":
            bot.reply_to(message, '\n\n'.join(less))
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, '\n\n'.join(less))
        else:
            bot.reply_to(message, '\n\n'.join(less))
    except:
        print(traceback.format_exc())
        if message.from_user.language_code == "uk":
            bot.send_message(chat_id=message.chat.id,text='Виникла помилка')
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,text='Произошла ошибка')
        else:
            bot.send_message(chat_id=message.chat.id,text='An error has occurred')


@bot.message_handler(commands=['tomorrow'])
def tomorrow(message):
    try:
        if message.text.startswith("Розклад на завтра") or message.text.startswith("Расписание на завтра") or message.text.startswith("Schedule for tomorrow"):
            if message.from_user.language_code == "uk":
                try:
                    args = message.text.split('Розклад на завтра ')[1]
                except:
                    args = ""
                print(args)
            elif message.from_user.language_code == "ru":
                try:
                    args = message.text.split('Расписание на завтра ')[1]
                except:
                    args = ""
                print(args)
            else:
                try:
                    args = message.text.split('Schedule for tomorrow ')[1]
                except:
                    args = ""
                print(args)
        else:
            args = extract_arg(message.text)
        st = Student.query.filter_by(tid=message.from_user.id).first()
        dt = datetime.now(ua_time) + timedelta(days=1)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0,tzinfo=None)  # Returns a copy
        less = []
        if len(args) > 0:
            lessons = Lessons.query.filter_by(group=''.join(args), date=dt).order_by(Lessons.order)
        else:
            st = Student.query.filter_by(tid=message.from_user.id).first()
            lessons = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
        if lessons.first() is None:
            text = f'{dt.strftime("%d.%m.%Y")}\nПар нет'
            less.append(text)
        else:
            less = aggregatio(lessons,less,dt)
        if message.from_user.language_code == "uk":
            bot.reply_to(message, '\n\n'.join(less))
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, '\n\n'.join(less))
        else:
            bot.reply_to(message, '\n\n'.join(less))
    except:
        print(traceback.format_exc())
        if message.from_user.language_code == "uk":
            bot.send_message(chat_id=message.chat.id,text='Виникла помилка')
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,text='Произошла ошибка')
        else:
            bot.send_message(chat_id=message.chat.id,text='An error has occurred')


@bot.message_handler(commands=['next_three_days'])
def next_three_days(message):
    try:
        if message.text.startswith("Розклад на три дні") or message.text.startswith("Расписание на три дня") or message.text.startswith("Schedule for three days"):
            if message.from_user.language_code == "uk":
                try:
                    args = message.text.split('Розклад на три дні ')[1]
                except:
                    args = ""
                print(args)
            elif message.from_user.language_code == "ru":
                try:
                    args = message.text.split('Расписание на три дня ')[1]
                except:
                    args = ""
                print(args)
            else:
                try:
                    args = message.text.split('Schedule for three days ')[1]
                except:
                    args = ""
                print(args)
        else:
            args = extract_arg(message.text)

        st = Student.query.filter_by(tid=message.from_user.id).first()
        td = datetime.now(ua_time)
        td = td.replace(hour=12, minute=0, second=0, microsecond=0,tzinfo=None)
        dt = datetime.now(ua_time) + timedelta(days=1)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0,tzinfo=None)
        tdat = datetime.now(ua_time) + timedelta(days=2)
        tdat = tdat.replace(hour=12, minute=0, second=0, microsecond=0,tzinfo=None)

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
            text = f'{td.strftime("%d.%m.%Y")}\nПар нет'
            less1.append(text)
        else:
            less1 = aggregatio(lessons1, less1, td)
        if lessons2.first() is None:
            text = f'{dt.strftime("%d.%m.%Y")}\nПар нет'
            less2.append(text)
        else:
            less2 = aggregatio(lessons2, less2, dt)
        if lessons3.first() is None:
            text = f'{tdat.strftime("%d.%m.%Y")}\nПар нет'
            less3.append(text)
        else:
            less3 = aggregatio(lessons3, less3, tdat)
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less1))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less2))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less3))
    except:
        print(traceback.format_exc())
        if message.from_user.language_code == "uk":
            bot.send_message(chat_id=message.chat.id,text='Виникла помилка')
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,text='Произошла ошибка')
        else:
            bot.send_message(chat_id=message.chat.id,text='An error has occurred')


@bot.message_handler(commands=['week'])
def week(message):
    try:
        if message.text.startswith("Розклад на тиждень") or message.text.startswith("Расписание на неделю") or message.text.startswith("Week schedule"):
            if message.from_user.language_code == "uk":
                try:
                    args = message.text.split('Розклад на тиждень ')[1]
                except:
                    args = ""
                print(args)
            elif message.from_user.language_code == "ru":
                try:
                    args = message.text.split('Расписание на неделю ')[1]
                except:
                    args = ""
                print(args)
            else:
                try:
                    args = message.text.split('Week schedule ')[1]
                except:
                    args = ""
                print(args)
            args = ""
        else:
            args = extract_arg(message.text)
        st = Student.query.filter_by(tid=message.from_user.id).first()
        dt = datetime.now(ua_time)
        dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)

        mnd = dt - timedelta(days=dt.weekday())
        monday = (dt - timedelta(days=dt.weekday()))
        tuesday = (mnd + timedelta(days=1))
        wednesday = (mnd + timedelta(days=2))
        thursday = (mnd + timedelta(days=3))
        friday = (mnd + timedelta(days=4))
        sunday = (mnd + timedelta(days=5))

        less1 = []
        less2 = []
        less3 = []
        less4 = []
        less5 = []
        less6 = []
        if len(args) > 0:
            lessons1 = Lessons.query.filter_by(group=''.join(args), date=monday).order_by(Lessons.order)
            lessons2 = Lessons.query.filter_by(group=''.join(args), date=tuesday).order_by(Lessons.order)
            lessons3 = Lessons.query.filter_by(group=''.join(args), date=wednesday).order_by(Lessons.order)
            lessons4 = Lessons.query.filter_by(group=''.join(args), date=thursday).order_by(Lessons.order)
            lessons5 = Lessons.query.filter_by(group=''.join(args), date=friday).order_by(Lessons.order)
            lessons6 = Lessons.query.filter_by(group=''.join(args), date=sunday).order_by(Lessons.order)
        else:
            lessons1 = Lessons.query.filter_by(group=st.group.name, date=monday).order_by(Lessons.order)
            lessons2 = Lessons.query.filter_by(group=st.group.name, date=tuesday).order_by(Lessons.order)
            lessons3 = Lessons.query.filter_by(group=st.group.name, date=wednesday).order_by(Lessons.order)
            lessons4 = Lessons.query.filter_by(group=st.group.name, date=thursday).order_by(Lessons.order)
            lessons5 = Lessons.query.filter_by(group=st.group.name, date=friday).order_by(Lessons.order)
            lessons6 = Lessons.query.filter_by(group=st.group.name, date=sunday).order_by(Lessons.order)
        if lessons1.first() is None:
            text = f'{monday.strftime("%d.%m.%Y")}\nПар нет'
            less1.append(text)
        else:
            less1 = aggregatio(lessons1, less1, monday)
        if lessons2.first() is None:
            text = f'{tuesday.strftime("%d.%m.%Y")}\nПар нет'
            less2.append(text)
        else:
            less2 = aggregatio(lessons2, less2, tuesday)
        if lessons3.first() is None:
            text = f'{wednesday.strftime("%d.%m.%Y")}\nПар нет'
            less3.append(text)
        else:
            less3 = aggregatio(lessons3, less3, wednesday)
        if lessons4.first() is None:
            text = f'{thursday.strftime("%d.%m.%Y")}\nПар нет'
            less4.append(text)
        else:
            less4 = aggregatio(lessons4, less4, thursday)
        if lessons5.first() is None:
            text = f'{friday.strftime("%d.%m.%Y")}\nПар нет'
            less5.append(text)
        else:
            less5 = aggregatio(lessons5, less5, friday)
        if lessons6.first() is None:
            text = f'{sunday.strftime("%d.%m.%Y")}\nПар нет'
            less6.append(text)
        else:
            less3 = aggregatio(lessons6, less6, sunday)
            # bot.reply_to(message, '\n'.join(less))
        bot.send_message(chat_id=message.chat.id,text='\n\n'.join(less1))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less2))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less3))
        bot.send_message(chat_id=message.chat.id,text='\n\n'.join(less4))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less5))
        bot.send_message(chat_id=message.chat.id, text='\n\n'.join(less6))
    except:
        print(traceback.format_exc())
        if message.from_user.language_code == "uk":
            bot.send_message(chat_id=message.chat.id,text='Виникла помилка')
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,text='Произошла ошибка')
        else:
            bot.send_message(chat_id=message.chat.id,text='An error has occurred')


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
            text = f'⏰{order} Урок {start} {end}'
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
    if message.from_user.language_code == "uk":
        msg = f'Користуватися ботом можна у двох режимах, перший за допомогою команд, другий за допомогою клавіатури (не можна переглядати групу без реєстрації). Команди: /today, /tomorrow, /next_three_days, /week, призначені для отримання розкладу на певний день. Мають дві форми: 1. Вихідна (/today) – призначена для отримання розкладу користувачеві, який був раніше зареєстрований. Доповнена (/today О1-20) – призначена для отримання розкладу для довільної групи (не вимагає реєстрації).\nДля реєстрації необхідно ввести команду /set і в наступному повідомленні вказати свою групу.\n'
    elif message.from_user.language_code == "ru":
        msg = f'Пользоваться ботом можно в двух режимах, первый с помощью команд, второй с помощью клавиатуры(недоступен просмотр группы без регистрации). Команды: /today, /tomorrow, /next_three_days, /week, предназначены для получения расписания на определенное к-во дней. Имеют две формы:\n 1. Исходная (/today) – предназначена для получения расписания пользователю, который был ранее зарегистрирован.\n2. Дополненная (/today О1-20) – предназначена для получения расписания для произвольной группы (не требует регистрацию).\nДля регистрации необходимо ввести команду /set и в следующем сообщении указать свою группу.\n'
    else:
        msg = f'Пользоваться ботом можно в двух режимах, первый с помощью команд, второй с помощью клавиатуры(недоступен просмотр группы без регистрации). Команды: /today, /tomorrow, /next_three_days, /week, предназначены для получения расписания на определенное к-во дней. Имеют две формы:\n 1. Исходная (/today) – предназначена для получения расписания пользователю, который был ранее зарегистрирован.\n2. Дополненная (/today О1-20) – предназначена для получения расписания для произвольной группы (не требует регистрацию).\nДля регистрации необходимо ввести команду /set и в следующем сообщении указать свою группу.\n'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    if message.text.startswith("Розклад на сьогодні") or message.text.startswith("Расписание на сегодня") or message.text.startswith("Schedule for today"):
        today(message)
    elif message.text.startswith("Розклад на завтра") or message.text.startswith("Расписание на завтра") or message.text.startswith("Schedule for tomorrow"):
        tomorrow(message)
    elif message.text.startswith("Розклад на три дні") or message.text.startswith("Расписание на три дня") or message.text.startswith("Schedule for three days"):
        next_three_days(message)
    elif message.text.startswith("Розклад на тиждень") or message.text.startswith("Расписание на неделю") or message.text.startswith("Week schedule"):
        week(message)
    elif message.text.startswith("Розклад дзвінків") or message.text.startswith("Расписание звонков") or message.text.startswith("Call Schedule"):
        calls(message)
    elif message.text.startswith("Змінити групу") or message.text.startswith("Сменить группу") or message.text.startswith("Change group"):
        setgroup(message)
    elif message.text.startswith("Моя група") or message.text.startswith("Моя группа") or message.text.startswith("My group"):
        group(message)
    elif message.text.startswith("Як користуватися ботом") or message.text.startswith("Как пользоваться ботом") or message.text.startswith("How to use a bot"):
        help(message)
    elif message.text.startswith("Вибрати групу") or message.text.startswith("Выбрать группу") or message.text.startswith("Set group"):
        setgroup(message)
    elif message.text.endswith(":00"):
        process_notification_step(message)
    elif message.text.startswith('◀️Назад') or message.text.startswith('◀️Назад') or message.text.startswith('◀ Back'):
        main_menu(message)
    elif message.text.startswith("Змiнити час отримання розкладу") or message.text.startswith("Изменить время получения расписания") or message.text.startswith("Change schedule notification"):
        notifi_change(message)
    elif message.text.startswith("⏹ Скинути") or message.text.startswith("⏹ Сбросить") or message.text.startswith("⏹ Reset"):
        reset(message)
    else:
        if message.from_user.language_code == "uk":
            msg = f'Невідома команда'
        elif message.from_user.language_code == "ru":
            msg = f'Неизвестная команда'
        else:
            msg = f'Unknown command'
        bot.send_message(message.chat.id, msg)


def process_group_step(message):
    try:
        st = Student.query.filter_by(tid=message.from_user.id).first()
        print(st)
        if st is None:
            group = Group.query.filter_by(name=message.text).first()
            get_or_create(db.session, Student, tid=message.from_user.id,
                          defaults={'first_name': message.from_user.first_name, 'username': message.from_user.username,
                                    'language_code': message.from_user.language_code, 'group': group, 'cid':message.chat.id})
        else:
            group = Group.query.filter_by(name=message.text).first()
            print(group.id)
            st.group = group
            st.group_id = group.id
            st.first_name = message.from_user.first_name
            st.username = message.from_user.username
            db.session.commit()
        if Group.query.filter_by(name=message.text).first() is None:
            if message.from_user.language_code == "uk":
                bot.reply_to(message, 'Такої групи не існує ')
            elif message.from_user.language_code == "ru":
                bot.reply_to(message, 'There is no such group')
            else:
                bot.reply_to(message, 'Group selected ')
        if message.from_user.language_code == "uk":
            bot.reply_to(message, 'Група обрана')
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, 'Группа выбрана')
        else:
            bot.reply_to(message, 'Group selected ')
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.from_user.language_code == "uk" or message.from_user.language_code == "ru":
            itemb = telebot.types.KeyboardButton("◀️Назад")
        else:
            itemb = telebot.types.KeyboardButton("◀ Back")
        if message.from_user.language_code == "uk":
            itemr = telebot.types.KeyboardButton("⏹ Скинути")
        elif message.from_user.language_code == "ru":
            itemr = telebot.types.KeyboardButton("⏹ Сбросить")
        else:
            itemr = telebot.types.KeyboardButton("⏹ Reset")
        item0 = telebot.types.KeyboardButton("6:00")
        item1 = telebot.types.KeyboardButton("7:00")
        item2 = telebot.types.KeyboardButton("8:00")
        item3 = telebot.types.KeyboardButton("9:00")
        item4 = telebot.types.KeyboardButton("10:00")
        item5 = telebot.types.KeyboardButton("11:00")
        item6 = telebot.types.KeyboardButton("12:00")
        item7 = telebot.types.KeyboardButton("13:00")
        item8 = telebot.types.KeyboardButton("14:00")
        item9 = telebot.types.KeyboardButton("15:00")
        item10 = telebot.types.KeyboardButton("16:00")
        item11 = telebot.types.KeyboardButton("17:00")
        item12 = telebot.types.KeyboardButton("18:00")
        item13 = telebot.types.KeyboardButton("19:00")
        item14 = telebot.types.KeyboardButton("20:00")
        item15 = telebot.types.KeyboardButton("21:00")
        item16 = telebot.types.KeyboardButton("22:00")
        item17 = telebot.types.KeyboardButton("23:00")
        markup.add(itemb,itemr,item0,item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,item11,item12,item13,item14,item15,item16,item17)
        if message.from_user.language_code == "uk":
            bot.send_message(chat_id=message.chat.id, text='Обери час коли ти хочешь отримувати розклад, ' + message.from_user.first_name,
                                 reply_markup=markup)
        elif message.from_user.language_code == "ru":
            bot.send_message(chat_id=message.chat.id,
                                 text='Выбери время когда ты хочешь получать расписание, ' + message.from_user.first_name,
                                 reply_markup=markup)
        else:
            bot.send_message(chat_id=message.chat.id,
                                 text='Choose time for notification ' + message.from_user.first_name,
                                 reply_markup=markup)
        bot.register_next_step_handler(message, process_notification_step)
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'oooops')


def process_notification_step(message):
    try:
        if message.text == '◀️Назад' or message.text =='◀ Back':
            main_menu(message)
            return
        elif message.text == '⏹ Сбросить' or message.text == "⏹ Скинути" or message.text == "⏹ Reset":
            st = Student.query.filter_by(tid=message.from_user.id).first()
            st.notification_time = datetime.now().time().replace(hour=0,minute=0,second=0,microsecond=0)
            db.session.commit()
            main_menu(message)
            return
        st = Student.query.filter_by(tid=message.from_user.id).first()
        print(st)
        st.notification_time = message.text
        st.cid = message.chat.id
        db.session.commit()
        if message.from_user.language_code == "uk":
            bot.reply_to(message, 'Час обраний')
        elif message.from_user.language_code == "ru":
            bot.reply_to(message, 'Время выбрано')
        else:
            bot.reply_to(message, 'Time selected')
    except Exception as e:
        print(traceback.format_exc())
        bot.reply_to(message, 'oooops')


def notifi_change(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.language_code == "uk" or message.from_user.language_code == "ru":
        itemb = telebot.types.KeyboardButton("◀️Назад")
    else:
        itemb = telebot.types.KeyboardButton("◀ Back")
    if message.from_user.language_code == "uk":
        itemr = telebot.types.KeyboardButton("⏹ Скинути")
    elif message.from_user.language_code == "ru":
        itemr = telebot.types.KeyboardButton("⏹ Сбросить")
    else:
        itemr = telebot.types.KeyboardButton("⏹ Reset")
    item0 = telebot.types.KeyboardButton("6:00")
    item1 = telebot.types.KeyboardButton("7:00")
    item2 = telebot.types.KeyboardButton("8:00")
    item3 = telebot.types.KeyboardButton("9:00")
    item4 = telebot.types.KeyboardButton("10:00")
    item5 = telebot.types.KeyboardButton("11:00")
    item6 = telebot.types.KeyboardButton("12:00")
    item7 = telebot.types.KeyboardButton("13:00")
    item8 = telebot.types.KeyboardButton("14:00")
    item9 = telebot.types.KeyboardButton("15:00")
    item10 = telebot.types.KeyboardButton("16:00")
    item11 = telebot.types.KeyboardButton("17:00")
    item12 = telebot.types.KeyboardButton("18:00")
    item13 = telebot.types.KeyboardButton("19:00")
    item14 = telebot.types.KeyboardButton("20:00")
    item15 = telebot.types.KeyboardButton("21:00")
    item16 = telebot.types.KeyboardButton("22:00")
    item17 = telebot.types.KeyboardButton("23:00")
    markup.add(itemb,itemr, item0, item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12,
               item13, item14, item15, item16, item17)
    if message.from_user.language_code == "uk":
        bot.send_message(chat_id=message.chat.id,
                         text='Обери час коли ти хочешь отримувати розклад, ' + message.from_user.first_name,
                         reply_markup=markup)
    elif message.from_user.language_code == "ru":
        bot.send_message(chat_id=message.chat.id,
                         text='Выбери время когда ты хочешь получать расписание, ' + message.from_user.first_name,
                         reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Choose time for notification ' + message.from_user.first_name,
                         reply_markup=markup)
    bot.register_next_step_handler(message, process_notification_step)


def reset(message):
    st = Student.query.filter_by(tid=message.from_user.id).first()
    st.notification_time = datetime.now().time().replace(hour=0,minute=0,second=0,microsecond=0)
    db.session.commit()
    if message.from_user.language_code == "uk":
        text = 'Час успішно скинуто'
    elif message.from_user.language_code == "ru":
        text = 'Время успешно сброшено'
    else:
        text = 'Success'
    bot.send_message(st.cid, f'{text}')


@app.route('/' + str(TOKEN), methods=['POST'])
def getMessage():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        flask.abort(403)


@app.route("/")
def webhook():
    bot.remove_webhook()
    if host.__contains__('vpu7'):
        bot.set_webhook(url=f'{host}' + TOKEN)
    else:
        bot.set_webhook(url=f'{host}' + TOKEN,certificate=open(WEBHOOK_SSL_CERT, 'r'))
    return "!", 200


@app.route("/sync")
def sync():
    req = requests.get(url='http://schedule.in.ua:3200/groups',
                       headers={'X-Institution': 'vische-profesiine-uchilische-7'})
    res = req.json()

    for r in res:
        group, create = get_or_create(db.session, Group, uid=r['_id'], name=r['name'])

    dt = datetime.today()
    if dt.isoweekday() == 7:
        db.session.query(Lessons).filter(Lessons.date <= dt).delete()
        db.session.commit()
        mnd = dt + timedelta(days=1)
        monday = (dt + timedelta(days=1)).strftime("%Y-%m-%d")
        sunday = (mnd + timedelta(days=5)).strftime("%Y-%m-%d")
    else:
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
                            headers={'X-Institution': 'vische-profesiine-uchilische-7','Content-Type': 'application/json'})
        res3 = orjson.loads(req3.data)
        print(g.name)
        print(len(res3))
        for d in res3:
            parseddate = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            # print(f'506 {parseddate}')
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


def main_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.language_code == "uk":
        item1 = telebot.types.KeyboardButton("Розклад на сьогодні")
        item2 = telebot.types.KeyboardButton("Розклад на завтра")
        item3 = telebot.types.KeyboardButton("Розклад на три дні")
        item4 = telebot.types.KeyboardButton("Розклад на тиждень")
        item5 = telebot.types.KeyboardButton("Розклад дзвінків")
        item6 = telebot.types.KeyboardButton("Змінити групу")
        item7 = telebot.types.KeyboardButton("Моя група")
        item8 = telebot.types.KeyboardButton("Як користуватися ботом")
        item9 = telebot.types.KeyboardButton("Змiнити час отримання розкладу")
        main_text = 'Головне меню'
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8,item9)
        bot.send_message(chat_id=message.chat.id, text='Привiт, ' + message.from_user.first_name, reply_markup=markup)
    elif message.from_user.language_code == "ru":
        item1 = telebot.types.KeyboardButton("Расписание на сегодня")
        item2 = telebot.types.KeyboardButton("Расписание на завтра")
        item3 = telebot.types.KeyboardButton("Расписание на три дня")
        item4 = telebot.types.KeyboardButton("Расписание на неделю")
        item5 = telebot.types.KeyboardButton("Расписание звонков")
        item6 = telebot.types.KeyboardButton("Сменить группу")
        item7 = telebot.types.KeyboardButton("Моя группа")
        item8 = telebot.types.KeyboardButton("Как пользоваться ботом")
        item9 = telebot.types.KeyboardButton("Изменить время получения расписания")
        main_text = 'Главное меню'
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8,item9)
        bot.send_message(chat_id=message.chat.id, text='Привет, ' + message.from_user.first_name, reply_markup=markup)
    else:
        item1 = telebot.types.KeyboardButton("Schedule for today")
        item2 = telebot.types.KeyboardButton("Schedule for tomorrow")
        item3 = telebot.types.KeyboardButton("Schedule for three days")
        item4 = telebot.types.KeyboardButton("Week schedule")
        item5 = telebot.types.KeyboardButton("Call Schedule")
        item6 = telebot.types.KeyboardButton("Change group")
        item7 = telebot.types.KeyboardButton("My group")
        item8 = telebot.types.KeyboardButton("How to use a bot")
        item9 = telebot.types.KeyboardButton("Change schedule notification")
        main_text = 'Main menu'
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8,item9)
    bot.send_message(chat_id=message.chat.id, text=f'{main_text}', reply_markup=markup)
    return


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


def test_job():
    st = Student.query.filter_by(notification_time=datetime.now(ua_time).time().replace(second=0, microsecond=0)).all()
    if datetime.now(ua_time).time().hour > 16:
        dt = datetime.now(ua_time) + timedelta(days=1)
    else:
        dt = datetime.now(ua_time)
    dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)  # Returns a copy
    for s in st:
        less = []
        lessons = Lessons.query.filter_by(group=st.group.name, date=dt).order_by(Lessons.order)
        if lessons.first() is None:
            text = f'{dt.strftime("%d.%m.%Y")}\nПар нет'
            less.append(text)
        else:
            less = aggregatio(lessons, less, dt)
        if datetime.now(ua_time).time().hour > 16:
            bot.send_message(chat_id=s.cid, text='Расписание на завтра \n\n'.join(less))
        else:
            bot.send_message(chat_id=s.cid, text='Расписание на сегодня \n\n'.join(less))


scheduler = BackgroundScheduler()
# job = scheduler.add_job(test_job, 'cron', day_of_week ='mon-sun', hour=16, minute=00)
# cron = '0,15,30,45 0-23 * * 1-6'
# cron = '0,15,30,45 6-23 * * 1-6'
job = scheduler.add_job(test_job, CronTrigger(day_of_week='mon-sun', hour='6-23', minute='0,15,30,45', timezone='Europe/Kiev'))
job2 = scheduler.add_job(sync, CronTrigger(day_of_week='sun', hour='8', minute='30', timezone='Europe/Kiev'))
scheduler.print_jobs()
scheduler.start()


def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)


@app.route('/')
def hello_world():
    return 'Hello World!'
