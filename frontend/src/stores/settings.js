import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { createI18n } from 'vue-i18n'
import zhCN from '../locales/zh-CN'
import en from '../locales/en'

export const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: { 'zh-CN': zhCN, en }
})

export const useSettingsStore = defineStore('settings', () => {
  const locale = ref(localStorage.getItem('locale') || 'zh-CN')
  const darkMode = ref(localStorage.getItem('darkMode') === 'true')

  function applyTheme() {
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  function setLocale(lang) {
    locale.value = lang
    localStorage.setItem('locale', lang)
    i18n.global.locale.value = lang
  }

  function toggleDarkMode(val) {
    darkMode.value = val
    localStorage.setItem('darkMode', val)
    applyTheme()
  }

  // 初始化
  applyTheme()
  i18n.global.locale.value = locale.value

  return { locale, darkMode, setLocale, toggleDarkMode, applyTheme }
})
