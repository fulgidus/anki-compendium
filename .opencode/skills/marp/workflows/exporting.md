# Exporting Marp Presentations

This workflow covers exporting Marp presentations to different formats for distribution and presentation.

---

## Export Formats

Marp supports multiple export formats:

- **PDF** — Best for distribution and printing
- **HTML** — Interactive web-based presentations
- **PPTX** — PowerPoint format for editing in Microsoft Office
- **PNG** — Individual slide images

---

## Prerequisites

- Marp CLI installed (`npm install -g @marp-team/marp-cli`)
- Completed Marp presentation (`.md` file)
- Images and assets referenced in presentation available

---

## Export to PDF

### Basic Export

```bash
marp presentation.md --pdf
```

Output: `presentation.pdf`

### Custom Output Path

```bash
marp presentation.md -o output/slides.pdf
```

### PDF with Specific Theme

```bash
marp presentation.md --pdf --theme custom-theme.css
```

### PDF Options

```bash
# Allow local file access for images
marp presentation.md --pdf --allow-local-files

# Set PDF metadata
marp presentation.md --pdf --pdf-notes --pdf-outlines
```

---

## Export to HTML

### Basic HTML Export

```bash
marp presentation.md --html
```

Output: `presentation.html`

### Self-Contained HTML

```bash
# Embed all assets (images, CSS) in single file
marp presentation.md --html --output standalone.html
```

### HTML with Navigation

```bash
# Enable navigation controls
marp presentation.md --html
```

The HTML output includes:
- Arrow key navigation
- Clickable progress bar
- Full-screen mode (F key)
- Print mode (Ctrl/Cmd + P)

---

## Export to PowerPoint (PPTX)

### Basic PPTX Export

```bash
marp presentation.md --pptx
```

Output: `presentation.pptx`

### Custom Output

```bash
marp presentation.md -o output/slides.pptx
```

**Note:** PPTX export has some limitations:
- Custom CSS may not fully translate
- Complex layouts might need adjustment
- Speaker notes are preserved

---

## Export to PNG (Images)

### Export All Slides as Images

```bash
marp presentation.md --images png
```

Output: `presentation.001.png`, `presentation.002.png`, etc.

### Custom Image Output Directory

```bash
marp presentation.md --images png -o output/
```

Output: `output/presentation.001.png`, etc.

### JPEG Format

```bash
marp presentation.md --images jpeg
```

---

## Export with Watch Mode

Auto-regenerate on file changes:

```bash
# Watch and export to PDF
marp presentation.md --pdf --watch

# Watch and export to HTML
marp presentation.md --html --watch
```

---

## Batch Export Multiple Formats

### Using Shell Script

```bash
#!/bin/bash
marp presentation.md --pdf -o output/slides.pdf
marp presentation.md --html -o output/slides.html
marp presentation.md --pptx -o output/slides.pptx
```

### Using Marp Config File

Create `marp.config.js`:

```javascript
module.exports = {
  inputDir: './slides',
  output: './output',
  pdf: true,
  html: true,
  pptx: true,
  allowLocalFiles: true
}
```

Run:
```bash
marp --config marp.config.js
```

---

## Custom Theme Export

### Export with Custom CSS Theme

```bash
marp presentation.md --pdf --theme-set custom-theme.css
```

### Inline Theme in Markdown

```markdown
---
marp: true
theme: custom
style: |
  section {
    background-color: #f0f0f0;
    color: #333;
  }
  h1 {
    color: #0066cc;
  }
---
```

---

## Advanced Export Options

### High-Quality PDF

```bash
# Export with higher resolution
marp presentation.md --pdf --allow-local-files --pdf-notes
```

### Export with Custom Size

```markdown
---
marp: true
size: 4:3
---
```

or

```markdown
---
marp: true
size: 16:9
---
```

### Export Specific Slides

Use Markdown comments to exclude slides from export:

```markdown
<!-- _class: skip -->
## Internal Notes Slide

This slide won't appear in final export
```

---

## Quality Checklist for Export

Before distributing exported presentations:

- [ ] Test PDF on different devices and PDF readers
- [ ] Verify all images display correctly
- [ ] Check font rendering (use web-safe fonts or embed)
- [ ] Test HTML in different browsers
- [ ] Ensure PPTX opens in PowerPoint/Google Slides
- [ ] Validate speaker notes are included (if needed)
- [ ] Check file size (optimize images if too large)
- [ ] Test links and interactive elements (HTML)

---

## Distribution Best Practices

### For PDF Distribution
- Optimize file size (compress images before adding)
- Include speaker notes if needed
- Use PDF/A format for archival

### For HTML Sharing
- Host on web server or GitHub Pages
- Ensure mobile responsiveness
- Test on different screen sizes

### For PPTX Editing
- Export early and often during development
- Test in PowerPoint before distributing
- Provide source `.md` file for version control

---

## Troubleshooting Export Issues

### Images Not Appearing
```bash
# Use --allow-local-files flag
marp presentation.md --pdf --allow-local-files
```

### Custom Fonts Not Rendering
```markdown
---
marp: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Roboto');
  section { font-family: 'Roboto', sans-serif; }
---
```

### Theme Not Applied
```bash
# Ensure theme file is in correct location
marp presentation.md --pdf --theme-set ./themes/custom.css
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Export Marp Presentation

on:
  push:
    paths:
      - 'presentation.md'

jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Export slides
        uses: docker://marpteam/marp-cli:latest
        with:
          args: presentation.md --pdf --html -o dist/
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: slides
          path: dist/
```

---

Your presentation is now ready for distribution in multiple formats! 📊
