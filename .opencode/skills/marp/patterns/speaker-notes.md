# Speaker Notes in Marp

This pattern guide covers how to add, format, and use speaker notes in Marp presentations.

---

## What Are Speaker Notes?

Speaker notes are hidden text visible only to the presenter, not shown on the slides themselves. They help you:

- Remember key talking points
- Include detailed explanations
- Add reminders for demos or transitions
- Store data sources and references
- Note timing or pacing suggestions

---

## Basic Syntax

Add speaker notes using HTML comments:

```markdown
## Slide Title

Content visible on slide

<!--
These are speaker notes.
Only visible in presenter mode.
-->

---
```

---

## Speaker Notes Best Practices

### Keep Notes Concise

```markdown
## Product Features

- Real-time collaboration
- AI-powered automation
- Enterprise security

<!--
KEY POINTS:
- Emphasize real-time = no delays
- AI demo: show automation workflow
- Security: mention SOC 2 compliance
-->
```

---

### Include Talking Points

```markdown
## Market Opportunity

$50B market growing at 25% YoY

<!--
TALKING POINTS:
1. Market size doubled in 3 years
2. SMB segment is underserved
3. Our TAM: $5B of the total market
4. Transition: "Now let's look at how we address this..."
-->
```

---

### Add Timing Reminders

```markdown
## Demo: Core Workflow

![width:800px](demo-screenshot.png)

<!--
DEMO (3 minutes):
- Login and dashboard (30s)
- Create new project (1m)
- Show collaboration features (1m)
- Q&A buffer (30s)

NOTE: Have backup video ready in case of technical issues
-->
```

---

### Reference Data Sources

```markdown
## Customer Growth

300% increase in Q4 2024

<!--
DATA SOURCE:
- Internal analytics dashboard
- Q4 2024 report (page 12)
- Verified by Finance team

CONTEXT:
- Previous quarter was 180%
- Industry average: 50%
-->
```

---

### Include Transition Cues

```markdown
<!-- _class: lead -->

# Section 2: Product Overview

<!--
TRANSITION:
"So we've established the market opportunity. Now let's dive into how our product uniquely solves these problems."

ENERGY: Increase enthusiasm here, this is the product reveal!
-->
```

---

## Viewing Speaker Notes

### In Marp for VS Code

1. Open presentation in VS Code
2. Click "Open Preview"
3. Speaker notes appear below each slide in preview mode

### In Exported HTML

```bash
marp presentation.md --html
```

1. Open generated HTML in browser
2. Press **P** key to toggle presenter mode
3. Speaker notes display in separate panel

### In PDF Export

```bash
# Include speaker notes in PDF
marp presentation.md --pdf --pdf-notes
```

Speaker notes appear on separate pages after each slide.

---

## Advanced Speaker Notes Patterns

### Multi-Section Notes

```markdown
## Complex Slide

Content here

<!--
INTRODUCTION:
Brief overview of what this slide covers

KEY POINTS:
1. First important point
2. Second important point
3. Third important point

OBJECTION HANDLING:
If asked about cost: "We're 30% more affordable than competitors"
If asked about timeline: "Implementation takes 2-4 weeks"

NEXT SLIDE:
Transition into customer success stories
-->
```

---

### Script-Style Notes

```markdown
## Opening Slide

<!--
SCRIPT:

"Good morning everyone, thank you for joining today's presentation.

My name is [NAME] and I'm excited to share with you how [PRODUCT] is revolutionizing [INDUSTRY].

Over the next 20 minutes, we'll cover three key areas:
- The market opportunity we're addressing
- Our unique solution and how it works
- Real-world results from our customers

Let's dive in."

[PAUSE FOR QUESTIONS]
-->
```

---

### Demo Instructions

```markdown
## Live Demo

<!--
DEMO CHECKLIST:
□ Browser open to demo.company.com
□ Test account logged in
□ Sample data loaded
□ Screen recording backup ready

STEPS:
1. Show dashboard overview (0:30)
2. Create new project (1:00)
   - Click "New Project" button
   - Fill in: Name="Demo Project", Type="Marketing"
   - Click "Create"
3. Demonstrate collaboration (1:30)
   - Invite team member (use demo@company.com)
   - Show real-time updates
   - Highlight commenting feature
4. Wrap up (0:30)
   - Return to dashboard
   - Transition to next slide

FALLBACK: If demo fails, use backup video at slide 15
-->
```

---

### Q&A Preparation

```markdown
## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Starter | $29/mo | Basic |
| Pro | $99/mo | Advanced |
| Enterprise | Custom | Full |

<!--
ANTICIPATED QUESTIONS:

Q: "What's included in the free trial?"
A: "All Pro features for 14 days, no credit card required."

Q: "Do you offer annual discounts?"
A: "Yes, 20% off when billed annually."

Q: "What's the cancellation policy?"
A: "Cancel anytime, no penalties. Data export included."

Q: "How does pricing scale for large teams?"
A: "Enterprise plans start at 50 users with volume discounts. Let's discuss your specific needs."
-->
```

---

### Slide Metadata

```markdown
## Customer Success Story

<!--
SLIDE INFO:
- Duration: 2 minutes
- Presenter: Sales lead
- Key message: Real ROI in 3 months
- Backup: Video testimonial if time permits

CONTEXT:
Customer: TechCorp Inc.
Industry: SaaS
Team size: 150 employees
Results: 300% productivity increase
-->
```

---

## Speaker Notes for Different Presentation Types

### Sales Pitch

```markdown
## Competitive Advantage

<!--
POSITIONING:
- We're the only solution with AI + collaboration
- 2x faster than competitors
- 50% lower cost than enterprise tools

PROOF POINTS:
- Case study: Company X saved $100K/year
- Analyst report: Ranked #1 in ease of use

OBJECTION HANDLING:
Price: "ROI achieved in 3 months on average"
Switching cost: "Free migration and training included"
-->
```

---

### Technical Presentation

```markdown
## Architecture Overview

![Architecture Diagram](architecture.png)

<!--
TECHNICAL DETAILS:
- Microservices architecture on Kubernetes
- PostgreSQL for OLTP, Snowflake for analytics
- Redis for caching and session management
- Event-driven using Apache Kafka

AUDIENCE NOTE:
Mix of technical and non-technical stakeholders.
Keep high-level, offer deep dive after.

DEMO AVAILABLE:
If time permits, show Grafana dashboards (link in notes)
-->
```

---

### Investor Pitch

```markdown
## Traction & Metrics

<!--
KEY METRICS (MEMORIZE):
- $2M ARR
- 150% net revenue retention
- 40% gross margin
- 300 customers, 15 enterprise

INVESTOR CONCERNS:
Burn rate: "18 months runway, breakeven in 12"
Competition: "We have proprietary IP, 3 patents pending"
Market size: "$50B TAM, $5B SAM"

ASK:
$5M Series A for product development and sales expansion
-->
```

---

## Speaker Notes Workflow

### During Presentation Creation

1. Write slide content first
2. Add speaker notes after each slide
3. Review notes for clarity and completeness
4. Rehearse presentation with notes visible

### During Rehearsal

1. Export to HTML with `marp --html`
2. Use presenter mode (press **P**)
3. Practice timing with notes visible
4. Refine notes based on rehearsal

### During Presentation

1. Use second screen for presenter view
2. Keep notes visible on laptop
3. Glance at notes, don't read verbatim
4. Use notes as prompts, not scripts

---

## Quality Checklist

Effective speaker notes should:

- [ ] Be concise and scannable
- [ ] Include key talking points, not full scripts
- [ ] Anticipate questions and objections
- [ ] Provide timing and pacing guidance
- [ ] Include demo steps or transitions
- [ ] Reference data sources and evidence
- [ ] Note backup plans for technical issues
- [ ] Be reviewed and updated before each presentation

---

Speaker notes transform your Marp slides into a complete presentation system! 🎤
