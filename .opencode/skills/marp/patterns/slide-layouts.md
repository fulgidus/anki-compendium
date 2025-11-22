# Marp Slide Layouts

This pattern library provides reusable slide layout templates for common presentation needs.

---

## 1. Title Slide (Lead)

**Use Case:** Opening slide, section dividers, major announcements

```markdown
<!-- _class: lead -->

# Main Title

## Subtitle or Tagline

**Presenter Name**  
*Date or Event*
```

**Characteristics:**
- Centered text
- Larger font sizes
- Minimal content
- High visual impact

---

## 2. Standard Content Slide

**Use Case:** General content, bullet points, key messages

```markdown
## Slide Heading

- Key point 1
- Key point 2
- Key point 3

Supporting text or explanation here.
```

**Best Practices:**
- Use `##` for slide title
- Max 5-7 bullet points
- Keep text concise
- Use visual hierarchy

---

## 3. Two-Column Layout

**Use Case:** Comparisons, before/after, pros/cons

```markdown
## Comparison Slide

<div class="columns">
<div>

### Column 1

- Point A
- Point B
- Point C

</div>
<div>

### Column 2

- Point X
- Point Y
- Point Z

</div>
</div>

<style>
.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
</style>
```

---

## 4. Image + Text Layout

**Use Case:** Visual storytelling, product features, screenshots

### Full-Width Image

```markdown
## Feature Showcase

![width:100%](feature-screenshot.png)

Brief description of the feature
```

### Split Layout (Image Right)

```markdown
## Product Demo

![bg right:40%](product-image.png)

- Feature 1
- Feature 2
- Feature 3
```

### Split Layout (Image Left)

```markdown
## Customer Story

![bg left:40%](customer-photo.png)

> "This product transformed our workflow"

**— Customer Name, Company**
```

---

## 5. Quote or Testimonial Slide

**Use Case:** Customer testimonials, inspirational quotes

```markdown
<!-- _class: lead -->

> "This is an impactful quote that spans multiple lines and captures attention."

**— Attribution, Company or Role**
```

**Alternative Style:**

```markdown
## Customer Success

<div style="background: #f0f0f0; padding: 2rem; border-left: 4px solid #0066cc;">

> "We saw 300% improvement in just 3 months."

</div>

**Sarah Johnson**  
*VP of Operations, TechCorp*
```

---

## 6. Data/Stats Slide

**Use Case:** Key metrics, statistics, impact numbers

```markdown
<!-- _class: lead -->

# 300%

## Growth in Q4 2024

---

## Key Metrics

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; text-align: center;">

<div>

### 10M+
Users

</div>

<div>

### 99.9%
Uptime

</div>

<div>

### $50M
Revenue

</div>

</div>
```

---

## 7. Table Layout

**Use Case:** Pricing, feature comparison, roadmap

```markdown
## Pricing Plans

| Feature | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Users | 5 | 50 | Unlimited |
| Storage | 10GB | 100GB | 1TB |
| Support | Email | Priority | Dedicated |
| **Price** | **$29/mo** | **$99/mo** | **Custom** |
```

**Styling Tables:**

```markdown
<style>
table {
  font-size: 0.9rem;
}
th {
  background-color: #0066cc;
  color: white;
}
</style>
```

---

## 8. Timeline Slide

**Use Case:** Roadmap, milestones, project phases

```markdown
## Launch Timeline

- **Q1 2024** — Beta Program Launch
- **Q2 2024** — Public Release
- **Q3 2024** — Enterprise Features
- **Q4 2024** — International Expansion
```

**Visual Timeline:**

```markdown
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">

<div style="text-align: center;">

**Q1**  
Beta

</div>

<div style="text-align: center;">

**Q2**  
Launch

</div>

<div style="text-align: center;">

**Q3**  
Enterprise

</div>

<div style="text-align: center;">

**Q4**  
Global

</div>

</div>
```

---

## 9. Process or Step-by-Step

**Use Case:** Workflows, instructions, methodology

```markdown
## Our Process

1. **Discovery** — Understand your needs
2. **Design** — Create tailored solution
3. **Develop** — Build and test
4. **Deploy** — Launch and support
```

**With Icons/Visuals:**

```markdown
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; text-align: center;">

<div>

### 1️⃣
**Analyze**

</div>

<div>

### 2️⃣
**Build**

</div>

<div>

### 3️⃣
**Launch**

</div>

</div>
```

---

## 10. Call-to-Action (CTA) Slide

**Use Case:** Next steps, contact info, engagement

```markdown
<!-- _class: lead -->

# Ready to Get Started?

## Sign up for free today

[www.product.com](https://www.product.com)

**Questions?** contact@product.com
```

**Alternative CTA:**

```markdown
## Next Steps

1. Schedule a demo: [Book Now](https://calendly.com/demo)
2. Download our guide: [Get PDF](https://link.com/guide)
3. Join our community: [Slack](https://slack.com/invite)

---

**Contact:** sales@company.com | +1-555-0100
```

---

## 11. Section Divider

**Use Case:** Breaking presentation into clear sections

```markdown
<!-- _class: lead -->
<!-- _backgroundColor: #0066cc -->
<!-- _color: white -->

# Part 2

## Customer Success Stories

---
```

---

## 12. Thank You / Questions Slide

**Use Case:** Closing slide, Q&A transition

```markdown
<!-- _class: lead -->

# Thank You!

## Questions?

**Contact:**  
john.doe@company.com  
@johndoe

---
```

---

## Layout Tips

### Alignment

```markdown
<!-- Use HTML for custom alignment -->

<div style="text-align: center;">
Centered content
</div>

<div style="text-align: right;">
Right-aligned content
</div>
```

### Spacing

```markdown
<div style="margin-top: 2rem;">
Content with top margin
</div>

<br><br>
<!-- Add vertical space -->
```

### Background Colors

```markdown
<!-- _backgroundColor: #f0f0f0 -->
Slide with light gray background

<!-- _backgroundColor: #0066cc -->
<!-- _color: white -->
Slide with blue background and white text
```

---

## Custom Layout Classes

Define reusable layout classes in frontmatter:

```markdown
---
marp: true
style: |
  .two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
  .highlight {
    background: #fff3cd;
    padding: 1rem;
    border-left: 4px solid #ffc107;
  }
---

<!-- _class: two-column -->
Content in two columns

<div class="highlight">
Highlighted callout box
</div>
```

---

Use these layouts as starting points and customize them to match your brand and content needs! 🎨
