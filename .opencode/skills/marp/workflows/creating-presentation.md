# Creating a Marp Presentation

This workflow guides you through creating a professional presentation using Marp.

---

## Prerequisites

- Marp CLI installed (`npm install -g @marp-team/marp-cli`) OR
- Marp for VS Code extension installed
- Basic Markdown knowledge
- Clear presentation outline and content

---

## Workflow Steps

### 1. Create the Markdown File

Create a new `.md` file for your presentation:

```bash
touch presentation.md
```

---

### 2. Add Frontmatter Configuration

Start your presentation with frontmatter to configure global settings:

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
color: #333333
---
```

**Common Frontmatter Options:**

| Option | Description | Example |
|--------|-------------|---------|
| `marp` | Enable Marp rendering | `true` |
| `theme` | Theme name | `default`, `gaia`, `uncover` |
| `paginate` | Show page numbers | `true` or `false` |
| `backgroundColor` | Default background color | `#ffffff` |
| `color` | Default text color | `#333333` |
| `size` | Slide size | `16:9` (default), `4:3` |
| `header` | Global header text | `'Company Name'` |
| `footer` | Global footer text | `'Confidential'` |

---

### 3. Create the Title Slide

Add a title slide with centered, large text:

```markdown
<!-- _class: lead -->

# Presentation Title

## Subtitle or Tagline

**Presenter Name**  
*Date*

---
```

**Directives Used:**
- `<!-- _class: lead -->` — Centers content and enlarges text

---

### 4. Add Content Slides

Structure your content with clear headings and concise bullet points:

```markdown
## Slide Heading

- Key point 1
- Key point 2
- Key point 3

---

## Another Slide

Content with **bold**, *italic*, and `code`.

![Image description](path/to/image.png)

---
```

**Best Practices:**
- One main idea per slide
- Use headings (`##`) for slide titles
- Keep bullet points short (max 7 words)
- Use visuals to support text

---

### 5. Add Section Dividers

Use section dividers to organize your presentation:

```markdown
<!-- _class: lead -->

# Section 2: Next Topic

---
```

---

### 6. Customize Individual Slides

Apply slide-specific styling with directives:

```markdown
<!-- _backgroundColor: #123456 -->
<!-- _color: #ffffff -->

## Slide with Custom Colors

White text on dark background

---

<!-- _backgroundImage: url('background.jpg') -->

## Slide with Background Image

---
```

---

### 7. Add Speaker Notes

Include speaker notes for presenter mode (not visible on slides):

```markdown
## Slide Title

Content on the slide

<!--
Speaker notes go here. These are only visible in presenter mode.
-->

---
```

---

### 8. Add Images and Media

Include images with sizing control:

```markdown
## Visual Slide

![width:500px](image.png)

![height:300px](chart.jpg)

![bg right](background-image.png)

---
```

**Image Directives:**
- `![width:500px](img.png)` — Set image width
- `![height:300px](img.png)` — Set image height
- `![bg](img.png)` — Use as background image
- `![bg right](img.png)` — Background on right side

---

### 9. Preview Your Presentation

**Using VS Code Extension:**
1. Open `.md` file in VS Code
2. Click "Open Preview" icon
3. Navigate slides with arrow keys

**Using Marp CLI:**
```bash
marp --preview presentation.md
```

---

### 10. Export Your Presentation

**Export to PDF:**
```bash
marp presentation.md --pdf
```

**Export to HTML:**
```bash
marp presentation.md --html
```

**Export to PowerPoint:**
```bash
marp presentation.md --pptx
```

**Export with Custom Output Name:**
```bash
marp presentation.md -o output/slides.pdf
```

---

## Example Complete Presentation

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #fff
---

<!-- _class: lead -->

# Product Launch 2024

## Introducing Our New Platform

**John Doe, Product Manager**  
*March 15, 2024*

---

## Agenda

1. Market Opportunity
2. Product Overview
3. Key Features
4. Go-to-Market Strategy
5. Next Steps

---

<!-- _class: lead -->

# Market Opportunity

---

## Market Size & Growth

- $50B market by 2025
- 25% YoY growth
- Underserved SMB segment

![width:600px](market-chart.png)

---

## Customer Pain Points

- **Problem 1**: Manual processes
- **Problem 2**: Lack of integration
- **Problem 3**: High costs

---

<!-- _class: lead -->

# Product Overview

---

## Product Vision

> Build the all-in-one platform that empowers teams to work smarter.

---

## Key Features

- ✅ Real-time collaboration
- ✅ AI-powered automation
- ✅ Seamless integrations
- ✅ Enterprise security

---

## Demo

![bg right](product-screenshot.png)

Live demonstration of core workflows

---

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Starter | $29/mo | Basic features |
| Pro | $99/mo | Advanced + AI |
| Enterprise | Custom | Full suite |

---

<!-- _class: lead -->

# Go-to-Market Strategy

---

## Launch Timeline

- **Q1**: Beta program
- **Q2**: Public launch
- **Q3**: Enterprise rollout
- **Q4**: International expansion

---

## Next Steps

1. Finalize beta feedback
2. Launch marketing campaign
3. Sales enablement training
4. Customer onboarding prep

---

<!-- _class: lead -->

# Questions?

**Contact:** john.doe@company.com

---
```

---

## Quality Checklist

Before finalizing your presentation:

- [ ] All slides have clear, concise headings
- [ ] Text is readable (sufficient contrast, font size)
- [ ] Images are high-quality and properly sized
- [ ] Consistent theme and styling throughout
- [ ] No spelling or grammar errors
- [ ] Speaker notes added where needed
- [ ] Exported to target format (PDF, HTML, PPTX)
- [ ] Tested on presentation device

---

## Tips for Effective Presentations

1. **Keep it Simple**: One idea per slide
2. **Visual Hierarchy**: Use size and color to guide attention
3. **Consistency**: Same fonts, colors, and layouts
4. **Less Text**: Use visuals and speak the details
5. **Storytelling**: Build a narrative arc
6. **Call to Action**: End with clear next steps

---

Your Marp presentation is now ready to deliver! 🎉
