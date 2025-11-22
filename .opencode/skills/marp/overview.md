# Marp Skill Overview

## Purpose

The Marp Skill provides comprehensive expertise in creating professional presentation slides using **Marp (Markdown Presentation Ecosystem)**. Marp enables version-controlled, text-based slide creation with powerful theming, layout control, and export capabilities.

---

## Core Competencies

### 1. Slide Structure & Syntax
- Writing slide content using Markdown syntax
- Separating slides with `---` dividers
- Using frontmatter for global slide configuration
- Applying slide-specific directives with `<!-- -->` comments
- Structuring content for visual clarity

### 2. Layout & Formatting
- Creating title slides, content slides, and section dividers
- Multi-column layouts with HTML/CSS
- Image placement and sizing
- Lists, tables, and code blocks
- Text alignment and positioning

### 3. Themes & Styling
- Applying built-in themes (default, gaia, uncover)
- Customizing themes with CSS
- Creating brand-specific color schemes
- Typography and font selection
- Background images and gradients

### 4. Advanced Features
- Speaker notes for presenter mode
- Slide-specific classes and styling
- Background colors and images per slide
- Page numbers and footers
- Transitions and animations (when supported)

### 5. Export & Distribution
- Exporting to PDF for distribution
- Generating HTML for web viewing
- Creating PowerPoint (PPTX) files
- Optimizing for print and screen
- Version control and collaboration

---

## Key Principles

### Simplicity
Presentations should be clean, focused, and easy to read. Avoid clutter and unnecessary visual noise.

### Consistency
Use consistent layouts, colors, and typography throughout the deck. Follow brand guidelines when applicable.

### Version Control
Markdown-based slides enable Git versioning, collaboration, and change tracking.

### Accessibility
Ensure sufficient contrast, readable font sizes, and clear visual hierarchy.

### Portability
Marp slides are plain text, making them platform-independent and easy to maintain.

---

## When to Use This Skill

Load the Marp Skill when:
- Creating business presentations (pitch decks, reports, proposals)
- Building technical documentation slides
- Designing marketing campaign decks
- Producing training and onboarding materials
- Generating product roadmap presentations
- Converting Markdown docs to slide format
- Building reusable presentation templates

---

## Integration with Other Skills

The Marp Skill often works alongside:
- **Content Writing Skill** — for narrative structure and storytelling
- **Copywriting Skill** — for persuasive messaging and CTAs
- **Brand Voice Skill** — for consistent tone and messaging
- **Design Skill** — for visual hierarchy and layout principles
- **Documentation Skill** — for technical accuracy and structure

---

## Supported Technologies

- **Marp CLI** — Command-line tool for rendering slides
- **Marp for VS Code** — Extension for live preview and editing
- **Marp Core** — Engine for Markdown-to-slide conversion
- **Themes** — Built-in (default, gaia, uncover) and custom CSS themes
- **Export Formats** — PDF, HTML, PPTX, PNG

---

## Quality Standards

All Marp presentations following this skill must meet:

- ✅ **Clarity**: Clear hierarchy, readable fonts, sufficient contrast
- ✅ **Consistency**: Uniform layouts, colors, and typography
- ✅ **Conciseness**: One idea per slide, minimal text, visual focus
- ✅ **Brand Alignment**: Follows brand colors, fonts, and style (when applicable)
- ✅ **Accessibility**: High contrast, readable font sizes, alt text for images
- ✅ **Version Control**: Stored in Git, with meaningful commit messages

---

## Marp Fundamentals

### Frontmatter Configuration

Every Marp presentation starts with frontmatter:

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #fff
color: #333
---
```

### Slide Separator

Slides are separated by `---`:

```markdown
# Slide 1

Content here

---

# Slide 2

More content

---
```

### Slide Directives

Control individual slides with HTML comments:

```markdown
<!-- _class: lead -->
# Title Slide

<!-- _backgroundColor: #123456 -->
## Slide with Custom Background
```

---

## Common Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `_class` | Apply custom CSS class | `<!-- _class: lead -->` |
| `_backgroundColor` | Set slide background | `<!-- _backgroundColor: #f0f0f0 -->` |
| `_color` | Set text color | `<!-- _color: #333 -->` |
| `_backgroundImage` | Set background image | `<!-- _backgroundImage: url('img.jpg') -->` |
| `_header` | Add header text | `<!-- _header: 'Company Name' -->` |
| `_footer` | Add footer text | `<!-- _footer: 'Confidential' -->` |
| `_paginate` | Show/hide page numbers | `<!-- _paginate: false -->` |

---

## Skill Structure

This skill contains:
- **workflows/** — Step-by-step procedures for creating presentations
- **patterns/** — Reusable slide templates and layout patterns
- **examples/** — Reference presentations for different use cases
- **troubleshooting/** — Common issues and resolutions

---

Use this skill to ensure Marp presentations are **professional, consistent, and impactful**.
