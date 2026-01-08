---
title: Standards and Metrics Framework
category: core
related:
  - ./llm-context-guide.md
  - ./comment-analysis/abuse-detection.md
  - ../platforms/twitter/comment-moderation.md
  - ../platforms/reddit/comment-moderation.md
---

# Standards and Metrics Framework

## Purpose

This document defines the moderation standards that govern comment approval, flagging, hiding, and removal across all platforms. Each standard is testable through specific metrics.

## Overview

The moderation framework consists of:
1. **Standards**: High-level moderation categories and definitions
2. **Metrics**: Testable criteria for each standard
3. **Actions**: Recommended moderation actions based on violations
4. **Severity Levels**: How serious a violation is

## Standard Categories

The system has **5 core standards**, each with specific metrics:

1. **Safety** - Protecting users from harm
2. **Quality** - Maintaining constructive discussion
3. **Spam** - Preventing unwanted promotional content
4. **Policy** - Platform-specific rules
5. **Engagement** - Healthy community interaction

---

## Standard 1: Safety

### Definition

Comments that threaten, harass, abuse, or incite harm against individuals or groups.

### Scope

Safety violations protect users from:
- Personal threats or violence
- Harassment or bullying
- Hate speech or discrimination
- Self-harm or dangerous behavior

### Metrics

#### 1.1 Direct Threats

**Definition**: Explicit statement of intent to harm

**Test Criteria**:
- Contains threat language ("I will...", "You should...", "Someone should...")
- Targets specific individual or group
- References violence, harm, or injury
- Conditional language ("If you...then...")

**Examples**:

✓ **VIOLATION**: "I'm going to get you for this"
- Explicit threat language: "I'm going to"
- Action: Targets the commenter
- Severity: HIGH

✓ **VIOLATION**: "All [group] should [violent action]"
- Group targeting: [group]
- Violent action specified
- Severity: CRITICAL

✗ **NOT VIOLATION**: "I disagree strongly with your opinion"
- No threat language
- No target
- Disagreement only

#### 1.2 Harassment and Bullying

**Definition**: Repeated, targeted negative comments designed to harm

**Test Criteria**:
- Pattern of negative comments toward target
- Personal attacks vs. criticism of ideas
- Intensity and persistence
- Public shaming or mockery

**Examples**:

✓ **VIOLATION**: "You're so stupid, nobody would ever like you"
- Personal attack (not idea criticism)
- Designed to hurt
- Severity: HIGH

✓ **VIOLATION**: [Repeated comments tagging someone in mocking context]
- Pattern of targeting
- Public shaming
- Severity: HIGH

✗ **NOT VIOLATION**: "I think your argument is flawed because..."
- Criticizes idea, not person
- Constructive tone
- Not designed to harm

#### 1.3 Hate Speech and Discrimination

**Definition**: Speech targeting protected characteristics

**Test Criteria**:
- References to protected characteristic (race, religion, gender, sexuality, disability)
- Dehumanizing language
- Slurs or epithets
- Claims of group inferiority

**Examples**:

✓ **VIOLATION**: [Explicit slur or dehumanizing language]
- Direct reference to slur
- Severity: CRITICAL

✓ **VIOLATION**: "[Group] are less [positive trait] than [group]"
- Claims inferiority based on characteristic
- Severity: HIGH

✗ **NOT VIOLATION**: "I have concerns about [policy] because..."
- Policy criticism
- No characteristic targeting
- Reasonable debate

#### 1.4 Dangerous or Illegal Content

**Definition**: Encouragement of illegal or dangerous behavior

**Test Criteria**:
- References to illegal activity
- Instructions for harmful behavior
- Encouragement of dangerous activity
- Links to illegal resources

**Examples**:

✓ **VIOLATION**: "Here's how to make [dangerous substance]"
- Explicit instructions
- Dangerous behavior
- Severity: CRITICAL

✓ **VIOLATION**: "You should [illegal action]"
- Encouragement of illegal act
- Severity: HIGH

✗ **NOT VIOLATION**: "I think this law is unjust because..."
- Criticism of law
- No encouragement of illegal action
- Policy discussion

### Moderation Actions

| Severity | Situation | Action |
|----------|-----------|--------|
| CRITICAL | Immediate danger or severe threats | **REMOVE** |
| HIGH | Targeted harassment, hate speech | **HIDE** + Flag for review |
| MEDIUM | Mild harassment, borderline threats | **FLAG** for review |
| LOW | Borderline case, ambiguous context | **FLAG** for review |

---

## Standard 2: Quality

### Definition

Comments that don't contribute meaningfully to discussion or follow community norms.

### Scope

Quality standards promote:
- On-topic conversation
- Constructive engagement
- Coherent and clear communication
- Effort and thoughtfulness

### Metrics

#### 2.1 Off-Topic Content

**Definition**: Comments not related to the post or discussion

**Test Criteria**:
- No semantic connection to post topic
- Introduces unrelated subject matter
- Derails conversation
- No connecting logic between post and comment

**Examples**:

✓ **VIOLATION**: [Post about cooking, comment about sports statistics]
- No semantic connection
- Different topic entirely
- Severity: MEDIUM

✗ **NOT VIOLATION**: [Post about cooking, comment about related recipe]
- Semantic connection
- Extends discussion
- On-topic

#### 2.2 Engagement Quality

**Definition**: Meaningful participation vs. low-effort comments

**Test Criteria**:
- Length and substance (comment length suggests effort)
- Contains question or response to other comments
- Adds new information or perspective
- Shows understanding of discussion

**Examples**:

✓ **VIOLATION**: "lol", "yes", "ok", "+1"
- Low effort
- No substance
- Severity: LOW (only flag if excessive)

✓ **Good**: "Great point about X. Have you considered Y?"
- Substantive
- References specific points
- Adds perspective
- No violation

#### 2.3 Coherence and Clarity

**Definition**: Comments should be understandable and reasonably coherent

**Test Criteria**:
- Uses understandable language
- Logical structure
- Clear intent or meaning
- Not spam-like repetition

**Examples**:

✓ **VIOLATION**: "jfkdsjf kdsjf dsjkf"
- Incoherent
- No meaning
- Severity: LOW

✗ **NOT VIOLATION**: "Your point about X is interesting, though I wonder about Y"
- Clear meaning
- Logical structure
- Coherent

---

## Standard 3: Spam

### Definition

Promotional content, repetitive posts, or manipulation tactics

### Scope

Spam standards prevent:
- Unwanted promotion of products/services
- Duplicate or near-duplicate posting
- Artificial engagement manipulation
- Bot-like behavior

### Metrics

#### 3.1 Promotional Content

**Definition**: Commercial or self-promotional material

**Test Criteria**:
- Includes links to external sites (especially new domains)
- Promotes product or service
- Calls to action (Buy, Visit, Click)
- MLM or recruitment language
- No genuine engagement with content

**Examples**:

✓ **VIOLATION**: "Check out my store! Buy now: [link]"
- Explicit promotion
- Call to action
- External link
- Severity: MEDIUM

✓ **VIOLATION**: "Join my fitness group! http://[domain]"
- Self-promotion
- Recruitment language
- External link
- Severity: MEDIUM

✗ **NOT VIOLATION**: "This reminds me of [relevant product], though I prefer Y"
- Mentions product but not promoting
- Engages with content
- No call to action
- Contextual relevance

#### 3.2 Repetition and Flooding

**Definition**: Same or near-identical comments posted repeatedly

**Test Criteria**:
- Duplicate or >80% similar to other recent comments
- Multiple comments in short time frame
- Pattern suggests automation
- Same content across multiple posts

**Examples**:

✓ **VIOLATION**: [Same comment posted 5 times in 10 minutes]
- Repetition
- Rapid posting
- Pattern of flooding
- Severity: HIGH (remove duplicates)

✓ **VIOLATION**: [Very similar promotional message in multiple posts]
- Near-duplicate content
- Across multiple posts
- Promotional pattern
- Severity: HIGH

✗ **NOT VIOLATION**: [Same comment posted once a day over a week]
- Not rapid flooding
- Might be genuine repeated concern
- Single instance
- Severity: LOW

#### 3.3 Link Density

**Definition**: Excessive links suggesting spam

**Test Criteria**:
- Multiple external links in single comment
- High ratio of links to text
- Links to new or suspicious domains
- Link shorteners or obfuscation

**Examples**:

✓ **VIOLATION**: "Check these 5 links! [link1] [link2] [link3]..."
- Multiple external links
- High link density
- Suspicious
- Severity: HIGH

✗ **NOT VIOLATION**: "This article helped me: [single relevant link]"
- One contextual link
- Relevant to discussion
- Normal behavior

### Moderation Actions

| Severity | Situation | Action |
|----------|-----------|--------|
| HIGH | Multiple links, multiple posts, flooding | **HIDE** or **REMOVE** |
| MEDIUM | Single promotional comment | **FLAG** or **HIDE** |
| LOW | Borderline promotional | **FLAG** for review |

---

## Standard 4: Policy

### Definition

Platform-specific rules and guidelines

### Scope

Policy violations are platform-dependent but generally cover:
- Impersonation and false identity
- Copyright and intellectual property
- Explicit/adult content
- Misinformation

### Metrics

#### 4.1 Impersonation

**Definition**: Falsely claiming to be someone else or misleading identity

**Test Criteria**:
- Claims to be public figure or company without verification
- Uses similar username/profile to impersonate
- Deceives others about identity
- Falsely implies endorsement

**Examples**:

✓ **VIOLATION**: Account pretending to be official company
- False identity claim
- Potential for deception
- Severity: HIGH

✗ **NOT VIOLATION**: "I'm John Smith" (common name, no impersonation context)
- Not impersonating anyone specific
- Generic name
- No deception

#### 4.2 Explicit or Adult Content

**Definition**: Sexually explicit or adult content (if policy prohibits)

**Test Criteria**:
- Graphic sexual descriptions
- Links to adult content
- Sexually explicit images/videos
- Unwarranted sexual advances

**Examples**:

✓ **VIOLATION**: [Explicitly sexual comment]
- Graphic sexual content
- Severity: MEDIUM (hide) or HIGH (remove)

✗ **NOT VIOLATION**: "The artistic nude photography in this post is striking"
- References adult content contextually
- Respectful discussion

#### 4.3 Misinformation

**Definition**: False information presented as fact

**Test Criteria**:
- Factually false statement
- Presented as fact
- Potential for harm
- Contradicts reliable sources

**Examples**:

✓ **VIOLATION**: "The vaccine causes autism [false claim]"
- Factually false
- Contradicts medical consensus
- Potential for harm
- Severity: HIGH

✗ **NOT VIOLATION**: "I don't think this approach will work because..."
- Opinion, not misinformation
- Clearly stated as belief

---

## Standard 5: Engagement

### Definition

Comments that support healthy community interaction

### Scope

Engagement standards promote:
- Respectful disagreement
- Constructive feedback
- Community building
- Positive participation

### Metrics

#### 5.1 Respectful Communication

**Definition**: Comments treat other users with basic respect

**Test Criteria**:
- Disagrees with ideas, not attacking person
- Uses respectful language even in disagreement
- Acknowledges other perspectives
- Avoids insults or condescension

**Examples**:

✓ **Good**: "I see your point, but I think there's another perspective: [perspective]"
- Respectful tone
- Acknowledges other view
- Adds perspective

✓ **VIOLATION**: "Only an idiot would think that"
- Personal attack
- Condescending
- Severity: MEDIUM

#### 5.2 Constructive Feedback

**Definition**: Criticism that aims to improve, not just attack

**Test Criteria**:
- Identifies specific issue
- Suggests improvement or alternative
- Tone is helpful rather than mean-spirited
- Engages with content seriously

**Examples**:

✓ **Good**: "I think the argument about X is weak. Consider instead [alternative]"
- Specific criticism
- Constructive suggestion
- Helpful tone

✓ **VIOLATION**: "This post sucks"
- No specific criticism
- No constructive element
- Severity: LOW (low quality)

---

## Testing Standards: The Moderation Decision Framework

### Step 1: Analyze the Comment

| Question | What to Look For |
|----------|------------------|
| What is the literal text? | Exact wording, context clues |
| Who is being targeted? | Specific individual, group, or general |
| What is the intent? | Harm, promotion, honest expression, humor |
| What is the context? | Post topic, conversation history |
| What platform is this? | Different rules apply |

### Step 2: Check Each Standard

For each standard, ask: **Does this comment violate this standard?**

```
Safety:     Does it threaten, harass, or incite harm?
Quality:    Is it on-topic and constructively expressed?
Spam:       Is it promotional or repetitive?
Policy:     Does it violate platform-specific rules?
Engagement: Is it respectfully communicated?
```

### Step 3: Assign Violation Scores

For each violated standard, assign severity:
- **CRITICAL**: Immediate danger, severe hate speech, serious threats
- **HIGH**: Targeted harassment, dangerous content, severe policy violations
- **MEDIUM**: Clear violations, meaningful harm potential
- **LOW**: Borderline cases, ambiguous context, minor violations

### Step 4: Make Moderation Decision

```
No violations:              APPROVE
1-2 LOW violations:         FLAG for review
1-2 MEDIUM violations:      HIDE + FLAG
Any HIGH violation:         HIDE + FLAG
Any CRITICAL violation:     REMOVE
Multiple violations:        Escalate to HIDE or REMOVE
```

### Step 5: Document Reasoning

Provide clear explanation:
- Which standards were violated
- Why they were violated (specific evidence)
- What severity level assigned
- What action recommended

---

## Examples: Testing Against Standards

### Example 1: Simple Approval

**Comment**: "Great explanation! I didn't understand that before but this clarifies it."

**Testing**:
- Safety: ✓ No threats, no harassment
- Quality: ✓ On-topic, constructive, substantive
- Spam: ✓ No promotion or repetition
- Policy: ✓ No policy violations
- Engagement: ✓ Respectful, constructive

**Decision**: **APPROVE**

---

### Example 2: Safety Violation

**Comment**: "People like you are ruining everything. You should [serious physical harm]"

**Testing**:
- Safety: ✗ CRITICAL - Explicit threat of physical harm
- Quality: N/A (already critical violation)
- Spam: ✓ No spam
- Policy: ✓ No specific policy violation
- Engagement: ✗ Hostile, disrespectful

**Decision**: **REMOVE** (Critical safety violation)

---

### Example 3: Spam Violation

**Comment**: "Check out my store! Great deals on [products]! http://mystore.com http://facebook.com/store http://instagram.com/store"

**Testing**:
- Safety: ✓ No threats or harassment
- Quality: ✗ MEDIUM - Off-topic promotional content
- Spam: ✗ HIGH - Multiple links, promotional language, call to action
- Policy: ✓ No specific policy violations (unless anti-spam is explicit)
- Engagement: ✗ No genuine engagement with post

**Decision**: **HIDE** (Clear spam violation)

---

### Example 4: Quality Violation

**Comment**: "ok", "lol", "agree"

**Testing**:
- Safety: ✓ No violations
- Quality: ✗ LOW - Low effort, minimal substance
- Spam: ✓ Not spam
- Policy: ✓ No violations
- Engagement: ✗ Minimal engagement

**Decision**: **FLAG** for review (Low quality, but relatively minor)

---

### Example 5: Policy Violation

**Comment**: "This is exactly like the time [explicit sexual scenario]..."

**Testing**:
- Safety: ✓ No threats or harassment
- Quality: ✓ On-topic, substantive
- Spam: ✓ Not spam
- Policy: ✗ HIGH - Explicit sexual content
- Engagement: ✓ Respectful tone

**Decision**: **HIDE** (Policy violation - explicit content)

---

## Creating Custom Standards

Organizations can extend these standards with custom rules:

### Template: Custom Standard

```markdown
## Standard [Name]: [Title]

### Definition
Clear one-sentence definition

### Scope
What this standard covers

### Metrics

#### [Number] [Metric Name]
**Definition**: What this metric measures
**Test Criteria**: How to identify violations
**Examples**: ✓ VIOLATION / ✗ NOT VIOLATION

### Moderation Actions
Recommended actions by severity
```

### Example: Community-Specific Standard

```markdown
## Standard 6: Community Guidelines

### Definition
Comments that violate our specific community values

### Scope
This applies to comments mentioning our community norms

### Metrics

#### 6.1 Inclusivity
Comments that exclude or dismiss community members

**Test Criteria**:
- Gatekeeping ("You're not a real X if...")
- Exclusionary language
- Dismissal of community members

#### 6.2 Evidence of Effort
For Q&A communities, questions should show research

**Test Criteria**:
- Shows problem-solving attempt
- Provides specific context
- Asks specific question (not vague)
```

---

## Standards by Platform

Standards apply across all platforms, but severity and priority may differ:

### Twitter/X
**Priority**: Safety, Engagement
- Real-time discussion culture
- Broad audiences
- High misinformation risk

### Reddit
**Priority**: Quality, Spam
- Community-focused
- Topic-specific discussions
- Strong anti-spam culture

### Instagram
**Priority**: Safety, Policy
- Visual content focus
- Younger audiences
- Strong brand safety

### YouTube
**Priority**: Safety, Spam, Policy
- Long-form content
- Wide audiences
- Strong copyright enforcement

### Medium
**Priority**: Quality, Spam
- Article-focused discussion
- Intellectual discourse
- Author protection

### TikTok
**Priority**: Safety, Policy
- Short-form video
- Younger audiences
- Rapid spread potential

---

## Testing Your Standards Understanding

### Quiz 1: Safety

**Comment**: "I hope something bad happens to [political figure]"

Is this a Safety violation?
- A) Yes, CRITICAL (threat of violence)
- B) Yes, HIGH (hoping for harm)
- C) No (just expressing frustration)
- D) Unclear

**Answer**: B - Yes, HIGH
Even though not an explicit threat, hoping for harm is harassment/abuse

---

### Quiz 2: Quality

**Comment**: "This is a good point about urban planning"

Is this a Quality violation?
- A) Yes, LOW (too short)
- B) Yes, MEDIUM (off-topic)
- C) No (substantive, on-topic)
- D) Unclear

**Answer**: C - No
Despite being brief, it's substantive and on-topic engagement

---

### Quiz 3: Spam

**Comment**: "Visit my blog at [link] for more tips!"

Is this a Spam violation?
- A) No (just sharing)
- B) Yes, LOW (self-promotion)
- C) Yes, MEDIUM (promotional content)
- D) Yes, HIGH (multiple violations)

**Answer**: C - Yes, MEDIUM
Self-promotional link with promotional language qualifies as spam

---

## Implementation

This framework is implemented through:

1. **Standards Engine** (`src/core/standards.py`)
   - Loads standard definitions
   - Validates comments against standards

2. **Metrics Validator** (`src/core/metrics.py`)
   - Calculates violation scores
   - Determines severity levels

3. **Analysis Modules** (`src/analysis/`)
   - Sentiment, categorization, abuse detection
   - Feed into standards validation

4. **Moderation Engine**
   - Combines all components
   - Makes final recommendations

---

## Review and Updates

This standards document should be reviewed:
- Quarterly for new patterns
- When platform policies change
- When community feedback indicates issues
- When violation patterns shift

---

**Document Version**: 1.0
**Last Updated**: January 2024
**Status**: Active
**Review Frequency**: Quarterly
