# Changelog

All notable changes to the frontend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-11-23

### Added
- **Centralized Error Handling Utility** - Created `utils/errors.ts` for consistent error message extraction
  - Handles Axios errors, FastAPI responses, network errors, and HTTP status codes
  - Prevents "[Object Object]" display by properly extracting error messages
  - Provides helper functions: `getErrorMessage()`, `isNetworkError()`, `isAuthError()`, etc.
  - Supports FastAPI `detail` field (string and validation array formats)

### Fixed
- **[Object Object] Error Display** - Fixed error messages showing "[Object Object]" instead of readable text
  - Updated all auth pages (LoginPage, RegisterPage) to use `getErrorMessage()`
  - Updated all Pinia stores (user, jobs, decks, dashboard) with proper error handling
  - Updated composables (usePdfUpload) to extract error messages correctly
  - Impact: Users now see clear, actionable error messages (e.g., "Email already registered", "Network error: Unable to reach server")

### Changed
- **Error Handling Pattern** - Standardized error extraction across entire codebase
  - Before: `error.response?.data?.detail || 'Fallback'`
  - After: `getErrorMessage(error, 'Fallback')`
  - Applied to 9 files with ~18 catch blocks updated

## [0.0.1] - 2025-11-23

### Fixed
- **Router Navigation Paths** - Fixed incorrect navigation paths in authentication pages
  - Updated RegisterPage.vue: Changed `/login` → `/auth/login` in success handler and "Sign In" link
  - Updated LoginPage.vue: Changed `/register` → `/auth/register` in "Create account" link
  - Root cause: Routes are nested under `/auth` parent route, but components were using root-level paths
  - Impact: Users can now properly navigate between login and register pages

### Context
- Register route is accessible at: `http://localhost:5173/auth/register`
- Login route is accessible at: `http://localhost:5173/auth/login`
- Both routes use AuthLayout.vue as parent component
