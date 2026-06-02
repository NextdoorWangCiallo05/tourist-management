import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './utils/request'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')

;(function() {
  const origErr = window.onerror
  window.onerror = function(msg, url, line, col, err) {
    if (typeof msg === 'string' && msg.includes('ResizeObserver loop')) return true
    if (err && err.message && err.message.includes('ResizeObserver loop')) return true
    return origErr ? origErr.apply(this, arguments) : false
  }
  const origAddEventListener = window.addEventListener.bind(window)
  window.addEventListener = function(type, handler, opts) {
    if (type === 'error') {
      const origHandler = handler
      handler = function(e) {
        if (e instanceof ErrorEvent && e.message && e.message.includes('ResizeObserver loop')) {
          e.preventDefault()
          e.stopPropagation()
          e.stopImmediatePropagation()
          return
        }
        return origHandler.apply(this, arguments)
      }
    }
    return origAddEventListener(type, handler, opts)
  }
  const origAppendChild = Node.prototype.appendChild
  Node.prototype.appendChild = function(child) {
    if (child && child.id === 'webpack-dev-server-client-overlay') {
      return child
    }
    return origAppendChild.call(this, child)
  }
})()