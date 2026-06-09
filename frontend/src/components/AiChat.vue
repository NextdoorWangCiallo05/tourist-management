<template>
  <div class="ai-chat" :class="{ expanded }">
    <button class="chat-toggle" @click="toggleChat" :title="expanded ? ($t('common.cancel') || '关闭助手') : 'AI'">
      <svg v-if="!expanded" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        <line x1="9" y1="10" x2="15" y2="10"/>
      </svg>
      <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>

    <div class="chat-panel" v-show="expanded">
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-avatar">AI</div>
          <div>
            <div class="chat-title">AI {{ $t('common.info') || '助手' }}</div>
            <div class="chat-status">{{ thinking ? ($t('common.loading') || '思考中...') : ($t('common.yes') ? 'Online' : '在线') }}</div>
          </div>
        </div>
        <button class="clear-btn" @click="clearChat" :title="$t('common.delete') || '清空'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>

      <div class="chat-messages" ref="msgList">
        <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
          <div class="msg-avatar">{{ m.role === 'user' ? '你' : 'AI' }}</div>
          <div class="msg-bubble">
            <div class="msg-text" v-html="renderMsg(m.content)"></div>
            <div class="msg-actions" v-if="m.role === 'assistant'">
              <button class="msg-action-btn" @click="retryMessage(i)" :title="$t('common.refresh') || '重新提问'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
              </button>
            </div>
          </div>
        </div>
        <div v-if="thinking" class="msg assistant">
          <div class="msg-avatar">AI</div>
          <div class="msg-bubble thinking">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="input"
          :placeholder="$t('common.placeholder') || '问点什么...'"
          :disabled="thinking"
          @keyup.enter="send"
          size="large"
        >
          <template #suffix>
            <button class="send-btn" @click="send" :disabled="!input.trim() || thinking">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </template>
        </el-input>
      </div>

      <div class="chat-hints" v-if="messages.length <= 1">
        <button v-for="h in hints" :key="h.key" class="hint-btn" @click="quickAsk(h.label)">{{ h.label }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import request from '../utils/request'

const { t } = useI18n()
const STORAGE_KEY = 'ai_chat_messages'
const MAX_MSGS = 50

const expanded = ref(false)
const input = ref('')
const messages = ref([])
const thinking = ref(false)
const msgList = ref(null)

const hints = [
  { key: 'groups', label: t('nav.tourGroups') || '查看旅游团' },
  { key: 'stats', label: (t('nav.dashboard') || '系统概览').includes('Dashboard') ? 'System Overview' : '系统概览' },
  { key: 'anomalies', label: t('common.warning') === '警告' ? '异常检测' : 'Anomaly Check' },
  { key: 'fee', label: t('common.info') === '信息' ? '取消手续费规则' : 'Cancel Fee Rules' },
]

// ── Markdown 渲染 ────────────────────────────────────────
const renderMsg = (text) => {
  if (!text) return ''
  let html = text
    // 转义 HTML
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // 粗体 **text**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码 `code`
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    // 表格：| a | b | -> <table>
    .replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim())
      if (cells.length === 0) return match
      // 检查是否是分隔行（|---|）
      if (cells.every(c => /^[\s\-:]+$/.test(c))) return ''
      return `<tr><td>${cells.join('</td><td>')}</td></tr>`
    })
    // 包裹表格
    .replace(/((?:\|<.+?\|[\s]*\n?)+)/g, '<table class="md-table">$1</table>')
    // 无序列表 - 开头的" · "或"- "
    .replace(/^[\s]*[•·\-]\s+(.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>[\s]*)+/g, '<ul class="md-list">$&</ul>')
    // 换行
    .replace(/\n/g, '<br>')
  return html
}

// ── 消息持久化 ──────────────────────────────────────────
const loadMessages = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length > 0) {
        messages.value = parsed
        return
      }
    }
  } catch (e) { /* ignore */ }
  // 默认欢迎语
  const isEn = t('nav.dashboard') === 'Dashboard'
  messages.value = [{
    role: 'assistant',
    content: isEn
      ? 'Hello! I can help you search tour groups, applications, stats, and more. Try the quick questions below!'
      : '👋 你好！我是 AI 助手，可以帮你查询旅游团、申请信息、统计数据等。试试下面的快捷提问～'
  }]
}

const saveMessages = () => {
  try {
    const toSave = messages.value.slice(-MAX_MSGS)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  } catch (e) { /* ignore */ }
}

const scrollDown = async () => {
  await nextTick()
  if (msgList.value) {
    msgList.value.scrollTop = msgList.value.scrollHeight
  }
}

// ── 发送消息 ────────────────────────────────────────────
const send = async () => {
  const text = input.value.trim()
  if (!text || thinking.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  thinking.value = true
  saveMessages()
  await scrollDown()

  try {
    // 传递最近 10 条对话上下文
    const context = messages.value.slice(-10).map(m => ({
      role: m.role, content: m.content
    }))
    const res = await request.post('/agent/chat', {
      message: text,
      context: context
    })
    messages.value.push({ role: 'assistant', content: res.reply || 'No reply' })
  } catch {
    messages.value.push({ role: 'assistant', content: 'Sorry, try again later.' })
  } finally {
    thinking.value = false
    saveMessages()
    await scrollDown()
  }
}

const quickAsk = (text) => {
  input.value = text
  send()
}

const retryMessage = (idx) => {
  // 找到对应的问题
  for (let i = idx - 1; i >= 0; i--) {
    if (messages.value[i]?.role === 'user') {
      input.value = messages.value[i].content
      return
    }
  }
}

const clearChat = () => {
  localStorage.removeItem(STORAGE_KEY)
  loadMessages()
  saveMessages()
}

const toggleChat = () => {
  expanded.value = !expanded.value
}

watch(expanded, async (val) => {
  if (val) await scrollDown()
})

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.ai-chat {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
}
.chat-toggle {
  width: 52px; height: 52px;
  border-radius: 50%;
  background: var(--accent, #4f6ef7);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(79, 110, 247, 0.35);
  transition: all 0.2s ease;
}
.chat-toggle:hover { transform: scale(1.05); box-shadow: 0 6px 24px rgba(79, 110, 247, 0.45); }

.chat-panel {
  position: absolute;
  bottom: 64px;
  right: 0;
  width: 380px;
  height: 520px;
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eef0f4);
  border-radius: 16px;
  box-shadow: var(--shadow-lg, 0 8px 40px rgba(0,0,0,0.12));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.2s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border, #eef0f4);
  background: var(--bg-card, #ffffff);
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent, #4f6ef7), #6366f1);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
}
.chat-title { font-size: 14px; font-weight: 600; color: var(--text-primary, #0b0f1a); }
.chat-status { font-size: 11px; color: #22c55e; }
.clear-btn {
  background: none; border: none; cursor: pointer; font-size: 16px;
  padding: 4px; border-radius: 6px; opacity: 0.5; color: var(--text-muted, #9ca3b0);
}
.clear-btn:hover { opacity: 1; background: var(--bg, #f8f9fc); }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--bg-card, #ffffff);
}
.msg { display: flex; gap: 8px; max-width: 90%; }
.msg.user { align-self: flex-end; flex-direction: row-reverse; }
.msg-avatar {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
}
.msg.user .msg-avatar { background: var(--accent, #4f6ef7); color: white; }
.msg.assistant .msg-avatar { background: var(--bg, #f1f5f9); color: var(--text-secondary, #5b677d); }
.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13.5px;
  line-height: 1.6;
  position: relative;
}
.msg.user .msg-bubble { background: var(--accent, #4f6ef7); color: white; }
.msg.assistant .msg-bubble { background: var(--bg, #f8f9fc); color: var(--text-primary, #0b0f1a); }
.msg-text { word-break: break-word; }

.msg-actions {
  position: absolute;
  bottom: -20px;
  right: 0;
  opacity: 0;
  transition: opacity 0.15s;
}
.msg-bubble:hover .msg-actions { opacity: 1; }
.msg-action-btn {
  background: var(--bg-card, white);
  border: 1px solid var(--border, #eef0f4);
  border-radius: 6px;
  padding: 2px 6px;
  cursor: pointer;
  color: var(--text-muted, #9ca3b0);
  display: flex;
  align-items: center;
}
.msg-action-btn:hover { color: var(--accent, #4f6ef7); }

.thinking { display: flex; gap: 4px; padding: 12px 18px !important; }
.dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--text-muted, #94a3b8); animation: bounce 1.4s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

.chat-input {
  padding: 10px 14px 8px;
  border-top: 1px solid var(--border, #eef0f4);
  background: var(--bg-card, #ffffff);
}
.chat-input :deep(.el-input__wrapper) {
  border-radius: 24px !important;
  padding: 2px 6px 2px 16px !important;
  background: var(--bg, #f8f9fc) !important;
}
.send-btn {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--accent, #4f6ef7); color: white;
  border: none; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  transition: all 0.15s ease;
}
.send-btn:disabled { opacity: 0.4; cursor: default; }
.send-btn:not(:disabled):hover { transform: scale(1.1); }

.chat-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 6px 14px 12px;
  background: var(--bg-card, #ffffff);
}
.hint-btn {
  padding: 5px 12px;
  border-radius: 14px;
  border: 1px solid var(--border, #eef0f4);
  background: var(--bg-card, white);
  font-size: 12px;
  color: var(--text-secondary, #5b677d);
  cursor: pointer;
  transition: all 0.15s ease;
}
.hint-btn:hover {
  border-color: var(--accent, #4f6ef7);
  color: var(--accent, #4f6ef7);
  background: var(--accent-soft, rgba(79,110,247,0.04));
}

/* Markdown 表格 */
:deep(.md-table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 12.5px;
}
:deep(.md-table td) {
  padding: 4px 8px;
  border: 1px solid var(--border, #eef0f4);
}
:deep(.md-table tr:first-child td) {
  font-weight: 600;
  background: var(--bg, #f8f9fc);
}
/* Markdown 列表 */
:deep(.md-list) { margin: 4px 0; padding-left: 16px; }
:deep(.md-list li) { margin: 2px 0; }
/* 行内代码 */
:deep(.inline-code) {
  background: var(--bg, #f1f5f9);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 12.5px;
  font-family: 'Consolas', 'Courier New', monospace;
}
</style>
