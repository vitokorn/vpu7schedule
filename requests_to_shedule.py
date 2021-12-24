import requests
import orjson
from datetime import datetime, timedelta
from app import Group, get_or_create, db,Lessons
import urllib3
http = urllib3.PoolManager()


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
