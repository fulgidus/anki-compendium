# Marp Themes and Styling

This pattern guide covers theme selection, customization, and styling best practices for Marp presentations.

---

## Built-in Themes

Marp provides three built-in themes:

### 1. Default Theme

```markdown
---
marp: true
theme: default
---
```

**Characteristics:**
- Clean, minimal design
- Good contrast
- Professional appearance
- Suitable for business and technical presentations

---

### 2. Gaia Theme

```markdown
---
marp: true
theme: gaia
---
```

**Characteristics:**
- Modern, bold design
- Vibrant colors
- Strong visual hierarchy
- Great for creative and marketing presentations

**Color Variants:**
```markdown
---
theme: gaia
class: lead  # Large centered text
---
```

---

### 3. Uncover Theme

```markdown
---
marp: true
theme: uncover
---
```

**Characteristics:**
- Elegant, sophisticated design
- Subtle animations
- High-end appearance
- Ideal for keynotes and executive presentations

---

## Custom Theme Basics

### Inline Custom Styling

Add custom CSS in the frontmatter:

```markdown
---
marp: true
style: |
  section {
    background-color: #f5f5f5;
    color: #333333;
  }
  h1 {
    color: #0066cc;
    border-bottom: 3px solid #0066cc;
  }
  h2 {
    color: #0099ff;
  }
---
```

---

## Brand Theme Template

Create a custom theme for your brand:

```markdown
---
marp: true
style: |
  /* Brand Colors */
  :root {
    --primary: #0066cc;
    --secondary: #ff6600;
    --background: #ffffff;
    --text: #333333;
    --accent: #00cc66;
  }

  /* Base Styles */
  section {
    background-color: var(--background);
    color: var(--text);
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }

  /* Headings */
  h1 {
    color: var(--primary);
    font-size: 3rem;
    font-weight: bold;
    border-bottom: 4px solid var(--primary);
    padding-bottom: 0.5rem;
  }

  h2 {
    color: var(--primary);
    font-size: 2rem;
    font-weight: 600;
  }

  h3 {
    color: var(--secondary);
    font-size: 1.5rem;
  }

  /* Links */
  a {
    color: var(--primary);
    text-decoration: none;
    border-bottom: 2px solid var(--primary);
  }

  a:hover {
    color: var(--secondary);
    border-bottom-color: var(--secondary);
  }

  /* Lists */
  ul, ol {
    font-size: 1.5rem;
  }

  li {
    margin-bottom: 0.5rem;
  }

  /* Code Blocks */
  code {
    background-color: #f0f0f0;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    color: var(--secondary);
  }

  pre {
    background-color: #2d2d2d;
    color: #f8f8f8;
    padding: 1rem;
    border-radius: 8px;
  }

  /* Tables */
  table {
    border-collapse: collapse;
    width: 100%;
  }

  th {
    background-color: var(--primary);
    color: white;
    padding: 0.75rem;
  }

  td {
    padding: 0.75rem;
    border-bottom: 1px solid #e0e0e0;
  }

  /* Lead Class (Title Slides) */
  section.lead {
    text-align: center;
    justify-content: center;
  }

  section.lead h1 {
    font-size: 4rem;
    border: none;
  }

  section.lead h2 {
    font-size: 2.5rem;
    color: var(--secondary);
  }

  /* Footer */
  footer {
    color: #888;
    font-size: 0.8rem;
  }

  /* Page Number */
  section::after {
    color: #888;
    font-size: 0.8rem;
  }
---
```

---

## External Theme File

For reusable themes, create a separate CSS file:

**custom-theme.css:**

```css
/* @theme custom */

@import 'default';

:root {
  --color-background: #ffffff;
  --color-foreground: #333333;
  --color-highlight: #0066cc;
  --color-accent: #ff6600;
}

section {
  background-color: var(--color-background);
  color: var(--color-foreground);
  font-family: 'Arial', sans-serif;
  font-size: 1.5rem;
}

h1 {
  color: var(--color-highlight);
  font-size: 3rem;
}

h2 {
  color: var(--color-highlight);
  font-size: 2rem;
}

section.lead {
  text-align: center;
}
```

**Use in presentation:**

```markdown
---
marp: true
theme: custom
---
```

**Export with custom theme:**

```bash
marp presentation.md --theme custom-theme.css --pdf
```

---

## Typography Best Practices

### Font Selection

```markdown
---
style: |
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  
  section {
    font-family: 'Roboto', sans-serif;
  }
  
  h1, h2, h3 {
    font-family: 'Roboto', sans-serif;
    font-weight: 700;
  }
---
```

### Font Sizes

| Element | Recommended Size | Use Case |
|---------|------------------|----------|
| `h1` | 2.5-4rem | Main titles, section dividers |
| `h2` | 1.8-2.5rem | Slide headings |
| `h3` | 1.3-1.8rem | Subheadings |
| Body | 1.2-1.5rem | Content text |
| Code | 1-1.2rem | Code blocks |

---

## Color Schemes

### High Contrast (Professional)

```css
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --primary: #0066cc;
  --secondary: #333333;
}
```

### Dark Theme

```css
:root {
  --bg: #1a1a1a;
  --text: #f0f0f0;
  --primary: #4da6ff;
  --secondary: #ff6600;
}

section {
  background-color: var(--bg);
  color: var(--text);
}
```

### Brand Colors Example

```css
/* Tech Startup */
:root {
  --primary: #6366f1;    /* Indigo */
  --secondary: #ec4899;  /* Pink */
  --accent: #10b981;     /* Green */
  --background: #ffffff;
  --text: #1f2937;
}

/* Corporate Blue */
:root {
  --primary: #003d82;
  --secondary: #0066cc;
  --accent: #00a3e0;
  --background: #ffffff;
  --text: #333333;
}
```

---

## Background Customization

### Solid Color Background

```markdown
<!-- _backgroundColor: #f0f0f0 -->
Slide with gray background
```

### Gradient Background

```markdown
<!-- _backgroundImage: linear-gradient(135deg, #667eea 0%, #764ba2 100%) -->
<!-- _color: white -->

# Slide with Gradient
```

### Image Background

```markdown
<!-- _backgroundImage: url('background.jpg') -->
<!-- _backgroundSize: cover -->
<!-- _color: white -->

# Slide with Image Background
```

### Semi-Transparent Overlay

```markdown
---
style: |
  section {
    background-image: url('bg.jpg');
    background-size: cover;
    position: relative;
  }
  
  section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
  }
---
```

---

## Layout Utilities

### Grid Layouts

```css
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
```

### Flexbox Utilities

```css
.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

---

## Special Effects

### Box Shadows

```css
.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Borders and Dividers

```css
.highlight-box {
  border-left: 4px solid #0066cc;
  padding-left: 1rem;
  background: #f0f8ff;
}
```

### Custom Bullets

```css
ul {
  list-style: none;
}

ul li::before {
  content: '✓ ';
  color: #00cc66;
  font-weight: bold;
  margin-right: 0.5rem;
}
```

---

## Responsive Design

Ensure presentations look good on different screen sizes:

```css
@media (max-width: 1024px) {
  section {
    font-size: 1.2rem;
  }
  
  h1 {
    font-size: 2.5rem;
  }
  
  h2 {
    font-size: 1.8rem;
  }
}
```

---

## Theme Checklist

When creating a custom theme:

- [ ] Define consistent color palette
- [ ] Set readable font sizes (min 1.2rem for body)
- [ ] Ensure sufficient contrast (WCAG AA: 4.5:1)
- [ ] Style all heading levels (h1, h2, h3)
- [ ] Customize links, code, tables
- [ ] Define `.lead` class for title slides
- [ ] Test on projector/large screen
- [ ] Export and review in target format

---

Use these styling patterns to create professional, brand-consistent presentations! 🎨
