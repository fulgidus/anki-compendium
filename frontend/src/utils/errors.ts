/**
 * Error handling utilities
 * 
 * Provides centralized error message extraction to prevent
 * "[Object Object]" display issues in the UI
 */

import type { AxiosError } from 'axios'

/**
 * Extract a human-readable error message from any error type
 * 
 * Handles:
 * - Axios errors with response data
 * - FastAPI error responses (detail field)
 * - Standard Error objects
 * - Network errors
 * - Unknown error types
 * 
 * @param error - The error object (any type)
 * @param fallback - Default message if no specific error found
 * @returns Human-readable error message string
 */
export function getErrorMessage(error: any, fallback = 'An unexpected error occurred'): string {
  // Null/undefined check
  if (!error) {
    return fallback
  }

  // FastAPI error format: response.data.detail (string or array)
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    
    // Detail can be a string
    if (typeof detail === 'string') {
      return detail
    }
    
    // Detail can be an array of validation errors
    if (Array.isArray(detail) && detail.length > 0) {
      // Extract first validation error
      const firstError = detail[0]
      if (firstError.msg) {
        return `${firstError.loc?.join('.') || 'Validation error'}: ${firstError.msg}`
      }
      return 'Validation error occurred'
    }
  }

  // Generic message field
  if (error.response?.data?.message) {
    return error.response.data.message
  }

  // Error field (some APIs use this)
  if (error.response?.data?.error) {
    return typeof error.response.data.error === 'string' 
      ? error.response.data.error 
      : fallback
  }

  // Standard Error object
  if (error.message && typeof error.message === 'string') {
    // Filter out generic Axios messages
    if (!error.message.startsWith('Request failed') && 
        !error.message.startsWith('Network Error')) {
      return error.message
    }
  }

  // Network error (no response received)
  if (error.request && !error.response) {
    return 'Network error: Unable to reach the server. Please check your connection.'
  }

  // HTTP status codes with meaningful messages
  if (error.response?.status) {
    switch (error.response.status) {
      case 400:
        return 'Bad request: Please check your input and try again'
      case 401:
        return 'Unauthorized: Please log in again'
      case 403:
        return 'Forbidden: You don\'t have permission to perform this action'
      case 404:
        return 'Not found: The requested resource doesn\'t exist'
      case 409:
        return 'Conflict: This resource already exists or is in use'
      case 422:
        return 'Validation error: Please check your input'
      case 429:
        return 'Too many requests: Please try again later'
      case 500:
        return 'Server error: Something went wrong on our end'
      case 502:
        return 'Bad gateway: The server is temporarily unavailable'
      case 503:
        return 'Service unavailable: Please try again later'
      case 504:
        return 'Gateway timeout: The request took too long'
      default:
        return `Error ${error.response.status}: ${fallback}`
    }
  }

  // Fallback message
  return fallback
}

/**
 * Extract error message from Axios error specifically
 * Type-safe version for Axios errors
 */
export function getAxiosErrorMessage(
  error: AxiosError,
  fallback = 'An unexpected error occurred'
): string {
  return getErrorMessage(error, fallback)
}

/**
 * Format validation errors from FastAPI into readable messages
 */
export function formatValidationErrors(errors: any[]): string[] {
  if (!Array.isArray(errors)) {
    return []
  }

  return errors.map(err => {
    const field = err.loc?.slice(1).join('.') || 'Unknown field'
    const message = err.msg || 'Validation error'
    return `${field}: ${message}`
  })
}

/**
 * Check if an error is a network error (no response from server)
 */
export function isNetworkError(error: any): boolean {
  return !!(error.request && !error.response)
}

/**
 * Check if an error is an authentication error (401 or 403)
 */
export function isAuthError(error: any): boolean {
  const status = error.response?.status
  return status === 401 || status === 403
}

/**
 * Check if an error is a validation error (400 or 422)
 */
export function isValidationError(error: any): boolean {
  const status = error.response?.status
  return status === 400 || status === 422
}

/**
 * Check if an error is a server error (5xx)
 */
export function isServerError(error: any): boolean {
  const status = error.response?.status
  return status >= 500 && status < 600
}
