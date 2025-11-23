# Changelog

All notable changes to the frontend will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
