# -*- coding: utf-8 -*-
"""示例数据注入脚本 - 处理中文编码"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db
from models import Route, TourGroup, User, AuditLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), display_name='王经理', role='admin')
        db.session.add(admin)

    routes_data = [
        {'route_code': 'YN-DL', 'route_name': '云南大理丽江经典5日游', 'description': '大理古城+洱海+丽江古城+玉龙雪山'},
        {'route_code': 'HA-SY', 'route_name': '海南三亚海岛5日游', 'description': '三亚海滩+蜈支洲岛+天涯海角'},
        {'route_code': 'BJ-GC', 'route_name': '北京古都文化4日游', 'description': '故宫+长城+颐和园+天坛'},
        {'route_code': 'GX-GL', 'route_name': '广西桂林山水4日游', 'description': '漓江+阳朔+十里画廊+象鼻山'},
        {'route_code': 'SC-JZ', 'route_name': '四川九寨沟仙境6日游', 'description': '九寨沟+黄龙+都江堰+宽窄巷子'},
    ]

    routes = {}
    for rd in routes_data:
        r = Route(route_code=rd['route_code'], route_name=rd['route_name'], description=rd['description'])
        db.session.add(r)
        db.session.flush()
        routes[rd['route_code']] = r.id

    groups_data = [
        {'route_code': 'YN-DL', 'departure': '2026-08-15', 'deadline': '2026-08-01', 'capacity': 30, 'adult': 3999, 'child': 1999},
        {'route_code': 'YN-DL', 'departure': '2026-09-10', 'deadline': '2026-08-25', 'capacity': 25, 'adult': 4299, 'child': 2199},
        {'route_code': 'HA-SY', 'departure': '2026-08-20', 'deadline': '2026-08-05', 'capacity': 35, 'adult': 3599, 'child': 1799},
        {'route_code': 'BJ-GC', 'departure': '2026-09-05', 'deadline': '2026-08-20', 'capacity': 40, 'adult': 2999, 'child': 1499},
        {'route_code': 'GX-GL', 'departure': '2026-07-25', 'deadline': '2026-07-10', 'capacity': 20, 'adult': 2799, 'child': 1399},
        {'route_code': 'SC-JZ', 'departure': '2026-08-28', 'deadline': '2026-08-15', 'capacity': 30, 'adult': 4599, 'child': 2299},
        {'route_code': 'HA-SY', 'departure': '2026-10-01', 'deadline': '2026-09-15', 'capacity': 45, 'adult': 4199, 'child': 2099},
    ]

    import random
    import string
    from models import Application, Participant, PaymentRecord
    def gen_code():
        return 'TG' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    def gen_app_no():
        return 'AP' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    group_ids = []
    for gd in groups_data:
        g = TourGroup(
            group_code=gen_code(),
            route_id=routes[gd['route_code']],
            departure_date=datetime.strptime(gd['departure'], '%Y-%m-%d').date(),
            deadline_date=datetime.strptime(gd['deadline'], '%Y-%m-%d').date(),
            max_capacity=gd['capacity'],
            adult_price=gd['adult'],
            child_price=gd['child'],
            is_public=True
        )
        db.session.add(g)
        db.session.flush()
        group_ids.append(g.id)

    db.session.commit()
    print(f'✅ 已创建 {len(routes_data)} 条路线 + {len(groups_data)} 个旅游团')

    now = datetime.now()
    sample_apps = [
        {'group_idx': 0, 'name': '张伟', 'phone': '13800001111', 'adult': 2, 'child': 1},
        {'group_idx': 2, 'name': '李娜', 'phone': '13800002222', 'adult': 1, 'child': 0},
        {'group_idx': 3, 'name': '王强', 'phone': '13800003333', 'adult': 2, 'child': 2},
    ]
    for sa in sample_apps:
        g = TourGroup.query.get(group_ids[sa['group_idx']])
        total = sa['adult'] * g.adult_price + sa['child'] * g.child_price
        deposit = round(total * 0.1, 2)
        app = Application(
            application_no=gen_app_no(), tour_group_id=g.id,
            responsible_name=sa['name'], responsible_phone=sa['phone'],
            adult_count=sa['adult'], child_count=sa['child'],
            deposit_amount=deposit, deposit_paid=True,
            balance_amount=round(total - deposit, 2),
            status='completed', completed_at=now
        )
        db.session.add(app)
        db.session.flush()

        for i in range(sa['adult'] + sa['child']):
            p = Participant(
                application_id=app.id,
                name=f'{sa["name"]}的参加者{i+1}',
                id_type='身份证', id_number=f'1101011990010{i+1}1234',
                is_adult=i < sa['adult'],
                phone_number=sa['phone']
            )
            db.session.add(p)

        payment = PaymentRecord(
            application_id=app.id, payment_type='deposit',
            amount=round(deposit, 2), paid_at=now
        )
        db.session.add(payment)

    db.session.commit()
    print(f'✅ 已创建 {len(sample_apps)} 条示例申请（含支付记录和参加者）')
    print(f'   默认账号: admin / admin123')
