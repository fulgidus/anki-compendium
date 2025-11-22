# Marp Troubleshooting Guide

Common issues and solutions when working with Marp presentations.

---

## Installation Issues

### Marp CLI Not Found

**Problem:** `marp: command not found`

**Solution:**
```bash
# Install Marp CLI globally
npm install -g @marp-team/marp-cli

# Verify installation
marp --version
```

**Alternative (using npx):**
```bash
npx @marp-team/marp-cli presentation.md --pdf
```

---

### VS Code Extension Not Working

**Problem:** Marp extension not rendering preview

**Solution:**
1. Install official extension: "Marp for VS Code"
2. Reload VS Code window (Cmd/Ctrl + Shift + P → "Reload Window")
3. Ensure file has `.md` extension
4. Check that frontmatter includes `marp: true`
5. Disable conflicting Markdown extensions

---

## Rendering Issues

### Images Not Displaying

**Problem:** Images don't appear in exported PDF/HTML

**Solution:**
```bash
# Use --allow-local-files flag
marp presentation.md --pdf --allow-local-files

# Or use absolute paths
![Image](file:///Users/username/images/photo.jpg)

# Or use relative paths from presentation location
![Image](./images/photo.jpg)
```

**Check:**
- Image file exists at specified path
- Image file extension is correct (.png, .jpg, .svg)
- No spaces in file path (or use quotes)

---

### Custom Fonts Not Rendering

**Problem:** Custom fonts don't display in exported files

**Solution:**

**Option 1: Use Web Fonts**
```markdown
---
marp: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  section {
    font-family: 'Roboto', sans-serif;
  }
---
```

**Option 2: Embed Fonts (Advanced)**
```bash
# Export with embedded fonts
marp presentation.md --pdf --allow-local-files
```

**Fallback:**
Use web-safe fonts:
- Arial, Helvetica, sans-serif
- Georgia, serif
- 'Courier New', monospace

---

### Theme Not Applied

**Problem:** Custom theme CSS not working

**Solution:**
```bash
# Ensure theme file path is correct
marp presentation.md --theme ./themes/custom.css --pdf

# Or specify theme in frontmatter
---
marp: true
theme: custom
---

# Then export with theme set
marp presentation.md --theme-set ./themes/custom.css --pdf
```

**Check:**
- Theme file starts with `/* @theme name */`
- Theme file is valid CSS
- Theme name matches frontmatter reference

---

### Slides Not Separating

**Problem:** All content on one slide

**Solution:**
- Ensure slide separator is `---` on its own line
- Add blank lines before and after `---`
- Check for typos (e.g., `--` instead of `---`)

```markdown
# Slide 1

Content here

---

# Slide 2

More content

---
```

---

## Layout Issues

### Content Overflowing Slide

**Problem:** Text or images overflow slide boundaries

**Solution:**
```markdown
<!-- Reduce content -->
<!-- Or adjust font size -->
<style>
section {
  font-size: 1.2rem;
}
</style>

<!-- Or scale images -->
![width:80%](large-image.png)

<!-- Or use smaller headings -->
## Instead of #
```

---

### Two-Column Layout Not Working

**Problem:** Columns not displaying side-by-side

**Solution:**
```markdown
<style>
.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
</style>

<div class="columns">
<div>

Column 1 content

</div>
<div>

Column 2 content

</div>
</div>
```

**Note:** Ensure proper blank lines around div tags and content.

---

### Background Image Not Covering Slide

**Problem:** Background image doesn't fill slide

**Solution:**
```markdown
<!-- _backgroundImage: url('bg.jpg') -->
<!-- _backgroundSize: cover -->
<!-- _backgroundPosition: center -->

# Slide Content
```

---

## Export Issues

### PDF Export Fails

**Problem:** `marp --pdf` produces error or blank PDF

**Solution:**
```bash
# Install required dependencies (Linux)
sudo apt-get install libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2

# macOS: Usually works out of the box
# Windows: Ensure Node.js and npm are up to date

# Try alternative export
marp presentation.md --html
# Then print HTML to PDF from browser
```

---

### PPTX Export Issues

**Problem:** PowerPoint export loses formatting

**Solution:**
- PPTX export has limitations
- Use PDF for distribution when formatting is critical
- Export to PPTX early and refine in PowerPoint
- Avoid complex CSS that won't translate

---

### HTML Export Missing Styles

**Problem:** HTML export doesn't include styles

**Solution:**
```bash
# Ensure styles are inline or embedded
marp presentation.md --html

# Check that style block is in frontmatter
---
marp: true
style: |
  section { ... }
---
```

---

### Large File Size

**Problem:** Exported PDF/HTML is too large

**Solution:**
1. **Compress images before adding:**
   ```bash
   # Using ImageOptim, TinyPNG, or:
   convert large.jpg -quality 85 -resize 1920x1080 optimized.jpg
   ```

2. **Use appropriate image formats:**
   - Photos: JPEG (compressed)
   - Graphics/logos: SVG or PNG
   - Avoid TIFF or BMP

3. **Optimize SVGs:**
   ```bash
   npm install -g svgo
   svgo input.svg -o output.svg
   ```

---

## Syntax Issues

### Markdown Not Rendering

**Problem:** Markdown syntax displaying as plain text

**Solution:**
- Check frontmatter has `marp: true`
- Ensure blank lines around Markdown elements
- Use proper Markdown syntax

```markdown
<!-- Correct -->
## Heading

- List item 1
- List item 2

<!-- Incorrect -->
## Heading
- List item 1
- List item 2
```

---

### HTML/CSS Not Working

**Problem:** HTML or CSS not rendering

**Solution:**
- Marp supports limited HTML/CSS
- Use `<div>`, `<style>`, `<span>` for basic layouts
- Complex JavaScript won't work
- Test in preview before exporting

---

### Speaker Notes Not Visible

**Problem:** Speaker notes don't appear in presenter mode

**Solution:**
```bash
# For HTML export, open and press 'P' key
marp presentation.md --html

# For PDF with notes
marp presentation.md --pdf --pdf-notes

# In VS Code, notes appear in preview pane
```

---

## Performance Issues

### Slow Preview in VS Code

**Problem:** Marp preview lags or freezes

**Solution:**
- Reduce number of slides in file
- Split large presentations into multiple files
- Optimize large images
- Disable other Markdown extensions
- Restart VS Code

---

### Slow Export

**Problem:** Export takes too long

**Solution:**
- Reduce image sizes before adding
- Use fewer custom fonts
- Simplify complex CSS
- Export to HTML first (faster), then PDF from browser

---

## Platform-Specific Issues

### Windows: Path Issues

**Problem:** Paths with backslashes don't work

**Solution:**
```markdown
<!-- Use forward slashes even on Windows -->
![Image](./images/photo.jpg)

<!-- Not backslashes -->
<!-- ![Image](.\images\photo.jpg) -->
```

---

### macOS: Permission Errors

**Problem:** "Permission denied" when exporting

**Solution:**
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm

# Or install Marp CLI with --unsafe-perm
sudo npm install -g @marp-team/marp-cli --unsafe-perm
```

---

### Linux: Missing Dependencies

**Problem:** Export fails with missing library errors

**Solution:**
```bash
# Install Chromium dependencies
sudo apt-get install -y \
  libnss3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libasound2
```

---

## Getting Help

If issues persist:

1. **Check Marp Documentation:**
   - https://marpit.marp.app/
   - https://github.com/marp-team/marp-cli

2. **Search GitHub Issues:**
   - https://github.com/marp-team/marp-cli/issues

3. **Verify Setup:**
   ```bash
   marp --version
   node --version
   npm --version
   ```

4. **Create Minimal Reproduction:**
   - Test with simplest possible presentation
   - Isolate the problematic feature
   - Report with steps to reproduce

---

Most Marp issues are related to paths, dependencies, or syntax. Use this guide to troubleshoot quickly! 🛠️
