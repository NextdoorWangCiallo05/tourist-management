<template>
  <div class="ai-chat" :class="{ expanded }">
    <button class="chat-toggle" @click="expanded = !expanded" :title="expanded ? '关闭助手' : '打开AI助手'">
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
            <div class="chat-title">AI 助手</div>
            <div class="chat-status">{{ thinking ? '思考中...' : '在线' }}</div>
          </div>
        </div>
        <button class="clear-btn" @click="clearChat" title="清空对话">🗑️</button>
      </div>

      <div class="chat-messages" ref="msgList">
        <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
          <div class="msg-avatar">{{ m.role === 'user' ? '你' : 'AI' }}</div>
          <div class="msg-bubble">
            <div class="msg-text" v-html="renderMsg(m.content)"></div>
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
          placeholder="问点什么..."
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
        <button v-for="h in hints" :key="h" class="hint-btn" @click="quickAsk(h)">{{ h }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import request from '../utils/request'

const expanded = ref(false)
const input = ref('')
const messages = ref([
  { role: 'assistant', content: '👋 你好！我是 AI 助手，可以帮你查询旅游团、申请信息、统计数据等。试试下面的快捷提问～' }
])
const thinking = ref(false)
const msgList = ref(null)

const hints = ['查看旅游团', '查询申请统计', '异常检测', '取消手续费规则']

const renderMsg = (text) => {
  return text
    .replace(/\n/g, '<br>')
    .replace(/  · /g, '&nbsp;&nbsp;· ')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
}

const scrollDown = async () => {
  await nextTick()
  if (msgList.value) {
    msgList.value.scrollTop = msgList.value.scrollHeight
  }
}

const send = async () => {
  const text = input.value.trim()
  if (!text || thinking.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  thinking.value = true
  await scrollDown()
  try {
    const res = await request.post('/agent/chat', { message: text })
    messages.value.push({ role: 'assistant', content: res.reply || '暂无回复' })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，我暂时无法回答，请稍后再试。' })
  } finally {
    thinking.value = false
    await scrollDown()
  }
}

const quickAsk = (text) => {
  input.value = text
  send()
}

const clearChat = () => {
  messages.value = [{ role: 'assistant', content: '👋 已清空，可以继续提问～' }]
}

watch(expanded, async (val) => {
  if (val) await scrollDown()
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
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.12);
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
  border-bottom: 1px solid #eef0f4;
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, #4f6ef7, #6366f1);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
}
.chat-title { font-size: 14px; font-weight: 600; color: #0b0f1a; }
.chat-status { font-size: 11px; color: #22c55e; }
.clear-btn { background: none; border: none; cursor: pointer; font-size: 16px; padding: 4px; border-radius: 6px; opacity: 0.5; }
.clear-btn:hover { opacity: 1; background: #f1f5f9; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg { display: flex; gap: 8px; max-width: 90%; }
.msg.user { align-self: flex-end; flex-direction: row-reverse; }
.msg-avatar {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; flex-shrink: 0;
}
.msg.user .msg-avatar { background: var(--accent, #4f6ef7); color: white; }
.msg.assistant .msg-avatar { background: #f1f5f9; color: #5b677d; }
.msg-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13.5px;
  line-height: 1.6;
}
.msg.user .msg-bubble { background: var(--accent, #4f6ef7); color: white; }
.msg.assistant .msg-bubble { background: #f8f9fc; color: #0b0f1a; }
.msg-text { word-break: break-word; }

.thinking { display: flex; gap: 4px; padding: 12px 18px !important; }
.dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #94a3b8; animation: bounce 1.4s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

.chat-input {
  padding: 10px 14px 8px;
  border-top: 1px solid #eef0f4;
}
.chat-input :deep(.el-input__wrapper) {
  border-radius: 24px !important;
  padding: 2px 6px 2px 16px !important;
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
}
.hint-btn {
  padding: 5px 12px;
  border-radius: 14px;
  border: 1px solid #eef0f4;
  background: white;
  font-size: 12px;
  color: var(--text-secondary, #5b677d);
  cursor: pointer;
  transition: all 0.15s ease;
}
.hint-btn:hover {
  border-color: var(--accent, #4f6ef7);
  color: var(--accent, #4f6ef7);
  background: rgba(79,110,247,0.04);
}
</style>
