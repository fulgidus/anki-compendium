import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import type { Deck, DeckFilters, DeckStats } from '@/types'

export const useDecksStore = defineStore('decks', () => {
  // State
  const decks = ref<Deck[]>([])
  const currentDeck = ref<Deck | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<DeckFilters>({
    search: '',
    sortBy: 'date',
    sortOrder: 'desc',
    tags: []
  })
  const stats = ref<DeckStats | null>(null)
  const statsLoading = ref(false)

  // Getters
  const filteredDecks = computed(() => {
    let result = [...decks.value]

    // Search filter
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      result = result.filter(deck => 
        deck.name.toLowerCase().includes(searchLower) ||
        deck.tags.some(tag => tag.toLowerCase().includes(searchLower))
      )
    }

    // Tags filter
    if (filters.value.tags && filters.value.tags.length > 0) {
      result = result.filter(deck =>
        filters.value.tags!.some(tag => deck.tags.includes(tag))
      )
    }

    // Sort
    const sortBy = filters.value.sortBy || 'date'
    const sortOrder = filters.value.sortOrder || 'desc'

    result.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name)
          break
        case 'cardCount':
          comparison = a.cardCount - b.cardCount
          break
        case 'date':
        default:
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return result
  })

  const totalDecks = computed(() => decks.value.length)

  const totalCards = computed(() => 
    decks.value.reduce((sum, deck) => sum + deck.cardCount, 0)
  )

  const allTags = computed(() => {
    const tagSet = new Set<string>()
    decks.value.forEach(deck => {
      deck.tags.forEach(tag => tagSet.add(tag))
    })
    return Array.from(tagSet).sort()
  })

  const getDeckById = computed(() => (id: string) => 
    decks.value.find(deck => deck.id === id)
  )

  // Actions
  const fetchDecks = async (customFilters?: DeckFilters): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const fetchedDecks = await api.getDecks(customFilters || filters.value)
      decks.value = fetchedDecks
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch decks'
      console.error('Error fetching decks:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchDeck = async (id: string): Promise<Deck | null> => {
    try {
      const deck = await api.getDeck(id)

      // Update in the list if it exists
      const index = decks.value.findIndex(d => d.id === id)
      if (index !== -1) {
        decks.value[index] = deck
      } else {
        decks.value.unshift(deck)
      }

      currentDeck.value = deck
      return deck
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch deck'
      console.error('Error fetching deck:', err)
      return null
    }
  }

  const deleteDeck = async (id: string): Promise<boolean> => {
    try {
      // Optimistic update
      decks.value = decks.value.filter(d => d.id !== id)

      await api.deleteDeck(id)

      if (currentDeck.value?.id === id) {
        currentDeck.value = null
      }

      return true
    } catch (err: any) {
      // Revert on error
      await fetchDecks()
      error.value = err.response?.data?.message || 'Failed to delete deck'
      console.error('Error deleting deck:', err)
      return false
    }
  }

  const deleteDecks = async (ids: string[]): Promise<boolean> => {
    try {
      // Optimistic update
      decks.value = decks.value.filter(d => !ids.includes(d.id))

      await api.deleteDecks(ids)

      if (currentDeck.value && ids.includes(currentDeck.value.id)) {
        currentDeck.value = null
      }

      return true
    } catch (err: any) {
      // Revert on error
      await fetchDecks()
      error.value = err.response?.data?.message || 'Failed to delete decks'
      console.error('Error deleting decks:', err)
      return false
    }
  }

  const downloadDeck = async (id: string, name: string): Promise<boolean> => {
    try {
      const blob = await api.downloadDeck(id)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${name}.apkg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to download deck'
      console.error('Error downloading deck:', err)
      return false
    }
  }

  const fetchStats = async (): Promise<void> => {
    statsLoading.value = true

    try {
      stats.value = await api.getDeckStats()
    } catch (err: any) {
      console.error('Error fetching deck stats:', err)
      // Don't set error for stats - it's not critical
    } finally {
      statsLoading.value = false
    }
  }

  const setFilters = (newFilters: Partial<DeckFilters>): void => {
    filters.value = {
      ...filters.value,
      ...newFilters
    }
  }

  const clearFilters = (): void => {
    filters.value = {
      search: '',
      sortBy: 'date',
      sortOrder: 'desc',
      tags: []
    }
  }

  const searchDecks = (query: string): void => {
    filters.value.search = query
  }

  const clearError = (): void => {
    error.value = null
  }

  const reset = (): void => {
    decks.value = []
    currentDeck.value = null
    loading.value = false
    error.value = null
    stats.value = null
    statsLoading.value = false
    clearFilters()
  }

  return {
    // State
    decks,
    currentDeck,
    loading,
    error,
    filters,
    stats,
    statsLoading,

    // Getters
    filteredDecks,
    totalDecks,
    totalCards,
    allTags,
    getDeckById,

    // Actions
    fetchDecks,
    fetchDeck,
    deleteDeck,
    deleteDecks,
    downloadDeck,
    fetchStats,
    setFilters,
    clearFilters,
    searchDecks,
    clearError,
    reset
  }
})
