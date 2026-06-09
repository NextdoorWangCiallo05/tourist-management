"""单元测试：纯业务函数（无数据库/HTTP 依赖）"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
from blueprints.groups import calc_deposit_rate
from blueprints.applications import calc_cancel_fee, gen_no
from blueprints.agent import tool_calculate_fee


# ── calc_deposit_rate ─────────────────────────────────────────

def test_deposit_rate_60_plus():
    """≥ 60 天 → 10%"""
    assert calc_deposit_rate(60) == 0.10
    assert calc_deposit_rate(90) == 0.10
    assert calc_deposit_rate(365) == 0.10


def test_deposit_rate_30_to_59():
    """30-59 天 → 20%"""
    assert calc_deposit_rate(30) == 0.20
    assert calc_deposit_rate(45) == 0.20
    assert calc_deposit_rate(59) == 0.20


def test_deposit_rate_under_30():
    """< 30 天 → 100%"""
    assert calc_deposit_rate(29) == 1.00
    assert calc_deposit_rate(15) == 1.00
    assert calc_deposit_rate(1) == 1.00
    assert calc_deposit_rate(0) == 1.00


# ── calc_cancel_fee ───────────────────────────────────────────

def test_cancel_fee_free():
    """≥ 30 天 → 免费"""
    assert calc_cancel_fee(30, 1000) == 0
    assert calc_cancel_fee(60, 5000) == 0


def test_cancel_fee_20_percent():
    """10-29 天 → 扣 20%"""
    assert calc_cancel_fee(10, 1000) == 200
    assert calc_cancel_fee(15, 2000) == 400
    assert calc_cancel_fee(29, 100) == 20


def test_cancel_fee_50_percent():
    """1-9 天 → 扣 50%"""
    assert calc_cancel_fee(1, 1000) == 500
    assert calc_cancel_fee(5, 2000) == 1000
    assert calc_cancel_fee(9, 100) == 50


def test_cancel_fee_same_day():
    """当天取消 → 扣 100%"""
    assert calc_cancel_fee(0, 1000) == 1000
    assert calc_cancel_fee(-5, 500) == 500


# ── gen_no ────────────────────────────────────────────────────

def test_gen_no_format():
    """申请编号格式：AP + 8 位大写字母+数字"""
    no = gen_no()
    assert no.startswith('AP')
    assert len(no) == 10
    assert re.match(r'^AP[A-Z0-9]{8}$', no)


def test_gen_no_uniqueness():
    """连续生成不应重复"""
    nos = {gen_no() for _ in range(100)}
    assert len(nos) == 100


# ── tool_calculate_fee ────────────────────────────────────────

def test_tool_fee_free():
    """≥ 30 天 → 免费"""
    result = tool_calculate_fee(30, 1000)
    assert result['fee'] == 0
    assert result['refund'] == 1000
    assert result['rate'] == '0%'


def test_tool_fee_20_percent():
    """10-29 天 → 扣 20%"""
    result = tool_calculate_fee(10, 1000)
    assert result['fee'] == 200.0
    assert result['refund'] == 800.0
    assert result['rate'] == '20%'


def test_tool_fee_50_percent():
    """1-9 天 → 扣 50%"""
    result = tool_calculate_fee(1, 1000)
    assert result['fee'] == 500.0
    assert result['refund'] == 500.0
    assert result['rate'] == '50%'


def test_tool_fee_full():
    """0 天（当天）→ 扣 100%"""
    result = tool_calculate_fee(0, 1000)
    assert result['fee'] == 1000
    assert result['refund'] == 0
    assert result['rate'] == '100%'


def test_tool_fee_edge_amounts():
    """边界金额测试"""
    result = tool_calculate_fee(10, 0)
    assert result['fee'] == 0.0
    assert result['refund'] == 0.0

    result = tool_calculate_fee(10, 1)
    assert result['fee'] == 0.2
    assert result['refund'] == 0.8
