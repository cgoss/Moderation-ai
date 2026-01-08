---
title: LLM Context Consumption Guide
category: core
related:
  - ../README.md
  - ./standards-and-metrics.md
  - ./api-reference/README.md
  - ./comment-analysis/README.md
---

# LLM Context Consumption Guide

## Purpose

This guide explains how Large Language Models (LLMs) should consume and utilize the Moderation AI context library to perform content moderation tasks across multiple social platforms.

## For LLM Systems

When you (an LLM) are asked to moderate content, analyze comments, or work with this library, follow this guide to effectively leverage the context library.

## Document Hierarchy

The library is organized hierarchically from general to specific:

### Level 1: Project Overview
**Start here for context**: [README.md](../README.md)
- Project vision and goals
- Quick start for users
- High-level feature overview
- Moderation capabilities summary

### Level 2: Core Concepts
These documents establish foundational understanding:

**For Moderation Understanding**:
- [standards-and-metrics.md](./standards-and-metrics.md)
  - What makes a comment "violating"?
  - How to test comments against standards
  - Definitions of moderation categories

**For Analysis Understanding**:
- [comment-analysis/README.md](./comment-analysis/README.md)
  - Available analysis techniques
  - How comments are categorized
  - Sentiment and tone detection
  - Abuse detection methodology

### Level 3: Technical Details

**For API Integration**:
- [api-reference/README.md](./api-reference/README.md)
  - How to interact with platform APIs
  - Authentication patterns
  - Rate limiting strategies

**For Platform-Specific Work**:
- `platforms/{platform}/README.md` (e.g., `platforms/twitter/README.md`)
  - Platform-specific capabilities
  - API structure and patterns
  - Data model specifics

### Level 4: Implementation Details

**For Detailed API Calls**:
- `platforms/{platform}/api-guide.md`
  - Endpoint specifications
  - Parameter definitions
  - Response structures

**For Implementation Examples**:
- `platforms/{platform}/examples/`
  - Concrete code patterns
  - Common workflows
  - Error handling examples

## Usage Patterns

### Pattern 1: Moderate a Single Comment

**Scenario**: User asks you to moderate a comment on Twitter

**Process**:
1. Read: [standards-and-metrics.md](./standards-and-metrics.md)
   - Understand what violations exist
   - Learn the metrics for testing

2. Read: [platforms/twitter/comment-moderation.md](../platforms/twitter/comment-moderation.md)
   - Understand Twitter-specific guidelines
   - Learn platform-specific considerations

3. Analyze the comment:
   - Check against each standard
   - Calculate violation scores
   - Determine recommended action

4. Execute via API:
   - Reference: [platforms/twitter/api-guide.md](../platforms/twitter/api-guide.md)
   - Determine appropriate API call
   - Execute moderation action

**Documentation sequence**:
```
standards-and-metrics.md
    ↓
platforms/twitter/comment-moderation.md
    ↓
platforms/twitter/api-guide.md
    ↓
Execute decision
```

### Pattern 2: Analyze Multiple Comments for Insights

**Scenario**: User asks for sentiment analysis across recent comments

**Process**:
1. Read: [comment-analysis/sentiment-analysis.md](./comment-analysis/sentiment-analysis.md)
   - Understand sentiment categories
   - Learn detection methodology
   - Review examples

2. Read: [comment-analysis/categorization.md](./comment-analysis/categorization.md)
   - Understand comment categories
   - Learn categorization rules

3. Read: Platform-specific data models
   - `platforms/{platform}/data-models.md`
   - Understand data structures

4. Analyze comments:
   - Apply sentiment analysis
   - Apply categorization
   - Aggregate results

**Documentation sequence**:
```
comment-analysis/sentiment-analysis.md
    ↓
comment-analysis/categorization.md
    ↓
platforms/{platform}/data-models.md
    ↓
Perform analysis
```

### Pattern 3: Extract Insights for Content Planning

**Scenario**: User asks "What should we create next based on comment feedback?"

**Process**:
1. Read: [comment-analysis/content-ideation.md](./comment-analysis/content-ideation.md)
   - Understand content suggestion methodology
   - Learn how to identify themes

2. Read: [comment-analysis/faq-extraction.md](./comment-analysis/faq-extraction.md)
   - Understand FAQ identification
   - Learn question patterns

3. Read: [comment-analysis/community-metrics.md](./comment-analysis/community-metrics.md)
   - Understand engagement metrics
   - Learn trend analysis

4. Extract insights:
   - Identify frequently asked topics
   - Find content gaps
   - Analyze community interests

**Documentation sequence**:
```
comment-analysis/content-ideation.md
    ↓
comment-analysis/faq-extraction.md
    ↓
comment-analysis/community-metrics.md
    ↓
Generate recommendations
```

### Pattern 4: Detect and Flag Harmful Content

**Scenario**: User asks "Is this comment abusive/bullying?"

**Process**:
1. Read: [comment-analysis/abuse-detection.md](./comment-analysis/abuse-detection.md)
   - Understand abuse types
   - Learn detection signals
   - Review examples

2. Read: [standards-and-metrics.md](./standards-and-metrics.md)
   - Find "Safety" and "Abuse" standards
   - Learn violation criteria

3. Read: Platform-specific moderation guidelines
   - `platforms/{platform}/comment-moderation.md`
   - Learn platform policies

4. Evaluate comment:
   - Check against abuse detection criteria
   - Check against standards
   - Determine severity

5. Execute action:
   - Reference: [platforms/{platform}/api-guide.md](../platforms/twitter/api-guide.md)
   - Flag, hide, or remove as appropriate

**Documentation sequence**:
```
comment-analysis/abuse-detection.md
    ↓
standards-and-metrics.md
    ↓
platforms/{platform}/comment-moderation.md
    ↓
platforms/{platform}/api-guide.md
    ↓
Execute action
```

## Document Characteristics

Each document in this library has specific characteristics to help LLM consumption:

### Metadata Header

Every document includes metadata:

```markdown
---
title: Document Title
category: [core|platform|api|analysis]
platform: [twitter|reddit|etc]  # If applicable
related:
  - path/to/related/doc.md
  - path/to/another/doc.md
---
```

**Use this to**:
- Understand document purpose quickly
- Find related documents
- Navigate to platform-specific info

### Clear Structure

Documents follow consistent structure:

```markdown
# Title

## Purpose
Explains why this document exists

## Key Concepts
Important terms and definitions

## Detailed Explanation
In-depth content

## Examples
Concrete examples

## Related Documentation
Links to related documents
```

### Concrete Examples

Every conceptual document includes examples:

```markdown
## Example: Detecting Spam

Comment: "Check out my site! http://spam.fake"

Analysis:
- Promotional content: ✓ (links to external site)
- Multiple links: ✗ (only one)
- Repetitive: ✗ (first mention)

Verdict: Spam (promotional content)
```

**Use examples to**:
- Understand abstract concepts
- Test your reasoning
- Verify your understanding

## Navigation Strategies

### Strategy 1: Question-Driven Navigation

When you have a question, find the answer:

| Question | Read This Document |
|----------|-------------------|
| "What are moderation standards?" | standards-and-metrics.md |
| "How do I authenticate with Twitter?" | platforms/twitter/authentication.md |
| "How do I detect spam?" | comment-analysis/abuse-detection.md |
| "What's the rate limit for Reddit?" | platforms/reddit/rate-limits.md |
| "How do I categorize comments?" | comment-analysis/categorization.md |

### Strategy 2: Task-Driven Navigation

When you have a task, follow the path:

**Task: Moderate a comment**
```
1. standards-and-metrics.md (understand violations)
2. platforms/{platform}/comment-moderation.md (platform rules)
3. Execute via Python library or API
```

**Task: Analyze sentiment**
```
1. comment-analysis/sentiment-analysis.md (methodology)
2. platforms/{platform}/data-models.md (data structures)
3. Execute analysis
```

**Task: Set up integration**
```
1. platforms/{platform}/README.md (overview)
2. platforms/{platform}/authentication.md (setup)
3. platforms/{platform}/api-guide.md (endpoints)
4. Implement integration
```

### Strategy 3: Platform-Focused Navigation

When working with a specific platform:

1. Start: `platforms/{platform}/README.md`
   - Platform overview
   - Capabilities and limits

2. Continue: `platforms/{platform}/api-guide.md`
   - API endpoints
   - Request/response formats

3. Reference: `platforms/{platform}/data-models.md`
   - Data structures
   - Field definitions

4. Apply: `platforms/{platform}/examples/`
   - Concrete code patterns
   - Common workflows

## Context Optimization Tips

### When Reading Documentation

1. **Start with the title and metadata**
   - Understand the document's purpose
   - Check related documents

2. **Read the key concepts section first**
   - Get definitions
   - Understand scope

3. **Scan the table of contents** (if present)
   - Find relevant sections
   - Skip what's not needed

4. **Review examples carefully**
   - Examples encode implementation details
   - Test your understanding against examples

5. **Follow the "related documentation" links**
   - Build mental connections
   - Understand the system holistically

### When Building Understanding

Build understanding in layers:

**Layer 1: Concepts**
- What is moderation?
- What are standards?
- What is sentiment analysis?

**Layer 2: Definitions**
- What specific standards exist?
- What are the metrics?
- How do we test against them?

**Layer 3: Implementation**
- How do we implement detection?
- What API calls do we make?
- What data structures are involved?

**Layer 4: Execution**
- Given a comment, what do we do?
- How do we integrate with Python library?
- How do we handle errors?

### When Reasoning About Moderation

Follow this reasoning pattern:

1. **Classify the comment**
   - What is it about? (topic/category)
   - What is the tone? (sentiment)
   - Who is the audience? (platform/context)

2. **Check against standards**
   - Does it violate Safety standard?
   - Does it violate Spam standard?
   - Does it violate Quality standard?
   - Does it violate Policy standard?

3. **Calculate violation score**
   - Severity of violations?
   - Number of violations?
   - Confidence in violations?

4. **Recommend action**
   - Approve (no violations)
   - Flag for review (minor violations)
   - Hide (moderate violations)
   - Remove (severe violations)

## Avoiding Common Mistakes

### Mistake 1: Reading Implementation Before Concepts

**Wrong approach**:
```
Jump directly to: platforms/twitter/api-guide.md
Without reading: standards-and-metrics.md
```

**Correct approach**:
```
1. Start: standards-and-metrics.md (understand what we're enforcing)
2. Then: platforms/twitter/comment-moderation.md (platform-specific rules)
3. Finally: platforms/twitter/api-guide.md (how to implement)
```

### Mistake 2: Ignoring Platform Differences

**Wrong**: Apply same moderation rules to all platforms

**Correct**: Read platform-specific moderation guidelines
- Understand platform culture and norms
- Apply platform-specific rules
- Adapt analysis approach for platform

### Mistake 3: Forgetting Context Windows

When working with multiple documents:
- Summarize key points from previous sections
- Reference key document sections by name
- Maintain consistency across analyses

### Mistake 4: Missing Examples

**Wrong**: Reason purely from definitions

**Correct**: Reason from definitions + validate against examples
- Use examples to ground understanding
- Test reasoning against example cases
- Adapt approach based on examples

## Document Modification Protocol

When you (as an LLM) generate documentation or code:

1. **Maintain consistent structure**
   - Follow existing patterns
   - Use the same metadata format
   - Use same heading hierarchy

2. **Include concrete examples**
   - Real-world cases
   - Both positive and negative examples
   - Enough detail to implement

3. **Link to related documents**
   - Help future LLMs navigate
   - Build the knowledge graph
   - Enable cross-reference

4. **Be precise with technical content**
   - Exact API parameters
   - Correct status codes
   - Accurate rate limits

## Integration with Python Library

The documentation complements the Python code:

**For API Integration**:
- Docs explain "what" to call
- Code implements "how" to call it
- Examples show "when" to call it

**For Analysis**:
- Docs explain methodology
- Code implements algorithm
- Tests validate correctness

**For Moderation**:
- Docs define standards
- Code validates against standards
- LLM reasoning applies standards

## Consuming Library APIs

When using the Python library:

1. **Read the docstrings**
   - Google-style docstrings
   - Parameters, returns, raises
   - Usage examples

2. **Check the type hints**
   - Parameter types
   - Return types
   - Help you understand contracts

3. **Read the tests**
   - Show expected behavior
   - Provide usage examples
   - Validate your understanding

4. **Reference the documentation**
   - Conceptual background
   - Why certain design choices
   - How components work together

## Quick Reference: Documentation Index

### Core Documentation
- [README.md](../README.md) - Project overview
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical design
- [standards-and-metrics.md](./standards-and-metrics.md) - Moderation standards
- [implementation-phases.md](./implementation-phases.md) - Development roadmap

### API Reference
- [api-reference/README.md](./api-reference/README.md) - API overview
- [api-reference/authentication.md](./api-reference/authentication.md) - Auth patterns
- [api-reference/rate-limiting.md](./api-reference/rate-limiting.md) - Rate limits
- [api-reference/error-handling.md](./api-reference/error-handling.md) - Error patterns

### Comment Analysis
- [comment-analysis/README.md](./comment-analysis/README.md) - Analysis overview
- [comment-analysis/sentiment-analysis.md](./comment-analysis/sentiment-analysis.md) - Sentiment detection
- [comment-analysis/abuse-detection.md](./comment-analysis/abuse-detection.md) - Abuse detection
- [comment-analysis/categorization.md](./comment-analysis/categorization.md) - Comment categorization
- [comment-analysis/faq-extraction.md](./comment-analysis/faq-extraction.md) - FAQ identification

### Platform-Specific
- [platforms/README.md](../platforms/README.md) - Platform overview
- [platforms/{platform}/api-guide.md](../platforms/twitter/api-guide.md) - Platform API guides
- [platforms/{platform}/authentication.md](../platforms/twitter/authentication.md) - Platform-specific auth
- [platforms/{platform}/examples/](../platforms/twitter/examples/) - Code examples

## Summary

As an LLM consuming this library:

1. **Understand the hierarchy**: General → Specific
2. **Follow the patterns**: Question-driven, Task-driven, or Platform-focused
3. **Use examples to validate**: Don't just read concepts
4. **Cross-reference**: Navigate via links to understand connections
5. **Apply consistently**: Same standards across platforms
6. **Reason clearly**: Show your work in moderation decisions

This library gives you the knowledge to moderate content effectively. Use it strategically to provide accurate, fair, and platform-appropriate moderation decisions.

---

**Document Version**: 1.0
**Last Updated**: January 2024
**Target Audience**: Large Language Models and AI Systems
