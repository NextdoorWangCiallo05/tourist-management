<template>
  <AppLayout activeMenu="settings" :breadcrumb="$t('settings.title')" :headerIcon="Setting">
    <div class="settings-grid">
      <div class="setting-card">
        <div class="setting-icon-wrap">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        </div>
        <div class="setting-body">
          <h3 class="setting-title">{{ $t('settings.language') }}</h3>
          <p class="setting-desc">{{ $t('settings.title') }} / Language</p>
          <div class="language-options">
            <button class="lang-btn" :class="{ active: settingsStore.locale === 'zh-CN' }" @click="switchLang('zh-CN')">
              <span class="lang-flag">🇨🇳</span>
              <span>{{ $t('settings.zh') }}</span>
            </button>
            <button class="lang-btn" :class="{ active: settingsStore.locale === 'en' }" @click="switchLang('en')">
              <span class="lang-flag">🇺🇸</span>
              <span>{{ $t('settings.en') }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="setting-card">
        <div class="setting-icon-wrap">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </div>
        <div class="setting-body">
          <h3 class="setting-title">{{ $t('settings.theme') }}</h3>
          <p class="setting-desc">{{ $t('settings.light') }} / {{ $t('settings.dark') }}</p>
          <div class="theme-options">
            <button class="theme-btn" :class="{ active: !settingsStore.darkMode }" @click="settingsStore.toggleDarkMode(false)">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              <span>{{ $t('settings.light') }}</span>
            </button>
            <button class="theme-btn" :class="{ active: settingsStore.darkMode }" @click="settingsStore.toggleDarkMode(true)">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              <span>{{ $t('settings.dark') }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="setting-card info-card">
        <div class="setting-icon-wrap">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </div>
        <div class="setting-body">
          <h3 class="setting-title">{{ $t('settings.title') }}</h3>
          <p class="setting-desc">{{ $t('settings.saved') }}</p>
          <div class="info-list">
            <div class="info-row"><span class="info-label">Version</span><span class="info-value">v1.0.0</span></div>
            <div class="info-row"><span class="info-label">Frontend</span><span class="info-value">Vue 3 + Vite 5</span></div>
            <div class="info-row"><span class="info-label">Backend</span><span class="info-value">Flask 2.3</span></div>
            <div class="info-row"><span class="info-label">{{ $t('settings.language') }}</span><span class="info-value">{{ settingsStore.locale === 'zh-CN' ? '中文' : 'English' }}</span></div>
            <div class="info-row"><span class="info-label">{{ $t('settings.theme') }}</span><span class="info-value">{{ settingsStore.darkMode ? $t('settings.dark') : $t('settings.light') }}</span></div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { Setting } from '@element-plus/icons-vue'
import { useSettingsStore } from '../stores/settings'
import AppLayout from '../components/AppLayout.vue'
import { ElMessage } from 'element-plus'

const settingsStore = useSettingsStore()

const switchLang = (lang) => {
  settingsStore.setLocale(lang)
  ElMessage.success(lang === 'zh-CN' ? '已切换至中文' : 'Switched to English')
}
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}
.setting-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 28px 24px;
  box-shadow: var(--shadow-sm);
  display: flex;
  gap: 18px;
}
.setting-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.setting-body { flex: 1; }
.setting-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 4px; }
.setting-desc { font-size: 13px; color: var(--text-muted); margin: 0 0 20px; }

.language-options, .theme-options {
  display: flex;
  gap: 10px;
}
.lang-btn, .theme-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.15s ease;
}
.lang-btn:hover, .theme-btn:hover { border-color: var(--accent); background: var(--accent-soft); }
.lang-btn.active, .theme-btn.active {
  border-color: var(--accent);
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}
.lang-flag { font-size: 18px; }

.info-card { grid-column: 1 / -1; }
.info-list { display: flex; flex-direction: column; gap: 8px; }
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg);
}
.info-label { font-size: 13px; color: var(--text-secondary); }
.info-value { font-size: 13px; color: var(--text-primary); font-weight: 500; }
</style>
