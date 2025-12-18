import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isCollapse = ref(false)
  const loading = ref(false)

  function toggleSidebar() {
    isCollapse.value = !isCollapse.value
  }

  function setLoading(value) {
    loading.value = value
  }

  return {
    isCollapse,
    loading,
    toggleSidebar,
    setLoading
  }
})
