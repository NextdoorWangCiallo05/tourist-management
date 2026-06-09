/**
 * 单元测试：前端纯函数
 * 测试状态映射、格式化函数、校验规则等无依赖的纯逻辑
 */
import { describe, test, expect } from 'vitest'

// ── 状态映射函数（来自 ApplicationList.vue）──────────────

function getStatusType(status) {
  const types = { pending: 'warning', completed: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { pending: '处理中', completed: '已完成', cancelled: '已取消' }
  return texts[status] || status
}

// ── 金额格式化函数 ──────────────────────────────────────

function fmt(n) {
  return Number(n || 0).toFixed(2)
}

// ── 校验规则正则（来自 Login.vue 注册表单）───────────────

const usernamePattern = /^[a-zA-Z0-9_\u4e00-\u9fa5]{2,20}$/
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const phonePattern = /^1[3-9]\d{9}$/

// ── getStatusType ────────────────────────────────────────

describe('getStatusType', () => {
  test('pending → warning', () => {
    expect(getStatusType('pending')).toBe('warning')
  })
  test('completed → success', () => {
    expect(getStatusType('completed')).toBe('success')
  })
  test('cancelled → danger', () => {
    expect(getStatusType('cancelled')).toBe('danger')
  })
  test('未知状态 → info（fallback）', () => {
    expect(getStatusType('unknown')).toBe('info')
    expect(getStatusType('')).toBe('info')
  })
})

// ── getStatusText ────────────────────────────────────────

describe('getStatusText', () => {
  test('pending → 处理中', () => {
    expect(getStatusText('pending')).toBe('处理中')
  })
  test('completed → 已完成', () => {
    expect(getStatusText('completed')).toBe('已完成')
  })
  test('cancelled → 已取消', () => {
    expect(getStatusText('cancelled')).toBe('已取消')
  })
  test('未知状态 → 原样返回', () => {
    expect(getStatusText('custom_status')).toBe('custom_status')
  })
})

// ── fmt ─────────────────────────────────────────────────

describe('fmt', () => {
  test('整数 → 保留两位小数', () => {
    expect(fmt(100)).toBe('100.00')
    expect(fmt(0)).toBe('0.00')
  })
  test('小数 → 保留两位', () => {
    expect(fmt(99.5)).toBe('99.50')
    expect(fmt(3.1415)).toBe('3.14')
  })
  test('null/undefined → 0.00', () => {
    expect(fmt(null)).toBe('0.00')
    expect(fmt(undefined)).toBe('0.00')
  })
  test('字符串数字 → 正确格式化', () => {
    expect(fmt('200')).toBe('200.00')
    expect(fmt('99.9')).toBe('99.90')
  })
})

// ── 用户名校验 ──────────────────────────────────────────

describe('username pattern', () => {
  test('合法用户名：字母数字下划线', () => {
    expect(usernamePattern.test('admin')).toBe(true)
    expect(usernamePattern.test('user_123')).toBe(true)
    expect(usernamePattern.test('张三')).toBe(true)
    expect(usernamePattern.test('abc')).toBe(true)
  })
  test('太短：少于2字符', () => {
    expect(usernamePattern.test('a')).toBe(false)
  })
  test('太长：超过20字符', () => {
    expect(usernamePattern.test('a'.repeat(21))).toBe(false)
  })
  test('含特殊字符', () => {
    expect(usernamePattern.test('user name')).toBe(false)
    expect(usernamePattern.test('user@name')).toBe(false)
    expect(usernamePattern.test('user.name')).toBe(false)
  })
})

// ── 邮箱校验 ────────────────────────────────────────────

describe('email pattern', () => {
  test('合法邮箱', () => {
    expect(emailPattern.test('user@example.com')).toBe(true)
    expect(emailPattern.test('test.user@company.cn')).toBe(true)
  })
  test('缺少 @', () => {
    expect(emailPattern.test('userexample.com')).toBe(false)
  })
  test('缺少域名', () => {
    expect(emailPattern.test('user@')).toBe(false)
    expect(emailPattern.test('user@.com')).toBe(false)
  })
  test('空字符串', () => {
    expect(emailPattern.test('')).toBe(false)
  })
})

// ── 手机号校验 ──────────────────────────────────────────

describe('phone pattern', () => {
  test('合法手机号（13-19开头）', () => {
    expect(phonePattern.test('13800138000')).toBe(true)
    expect(phonePattern.test('15912345678')).toBe(true)
    expect(phonePattern.test('19900001111')).toBe(true)
  })
  test('太短', () => {
    expect(phonePattern.test('1380013800')).toBe(false)
  })
  test('非1开头', () => {
    expect(phonePattern.test('23800138000')).toBe(false)
  })
  test('含字母', () => {
    expect(phonePattern.test('13800abc000')).toBe(false)
  })
})
