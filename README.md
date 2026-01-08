# Moderation AI - LLM Context Library for Content Moderation

A comprehensive context library and Python framework for instructing Large Language Models (LLMs) on how to moderate user-generated content across multiple social media platforms.

## Vision

Moderation AI provides LLMs with the knowledge, tools, and patterns needed to effectively moderate comments and content across Twitter/X, Reddit, Instagram, Medium, YouTube, and TikTok. This hybrid approach combines detailed markdown documentation (for LLM consumption) with a robust Python library (for programmatic automation).

The system enables:
- **Intelligent moderation decisions** powered by LLM reasoning
- **Cross-platform consistency** through unified standards and metrics
- **Efficient analysis** of large comment volumes through summarization and categorization
- **Community insights** including sentiment analysis, FAQ extraction, and content ideas
- **Abuse detection** to identify and flag bullying, spam, and harmful content

## Key Features

### 🎯 Moderation Capabilities
- **Standards & Metrics**: Testable moderation standards across all platforms
- **Comment Analysis**: Summarization, categorization, sentiment analysis
- **FAQ Extraction**: Identify frequently asked questions from comments
- **Content Ideation**: Discover follow-up content ideas from community feedback
- **Community Metrics**: Track engagement, reactions, and sentiment trends
- **Abuse Detection**: Identify bullying, harassment, and policy violations

### 📱 Multi-Platform Support
- **Twitter/X**: Real-time conversation monitoring and moderation
- **Reddit**: Community-focused discussion moderation
- **Instagram**: Visual content and caption moderation
- **Medium**: Article comment quality control
- **YouTube**: Video comment management at scale
- **TikTok**: Comment and creator interaction moderation

### 🤖 LLM-First Design
- All documentation in Markdown for native LLM consumption
- Context-optimized file organization and metadata
- Hierarchical structure from general to specific information
- Self-contained documents for focused LLM queries
- Examples and use cases in every conceptual document

### 🔧 Developer-Friendly
- Type-hinted Python code (Python 3.9+)
- Comprehensive test coverage (80%+ target)
- Well-documented API reference
- Clear contribution guidelines
- CI/CD pipelines for quality assurance

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cgoss/Moderation-ai.git
cd Moderation-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"
```

### Basic Usage

```python
from moderation_ai import ModerationEngine, StandardsValidator

# Initialize the moderation engine
engine = ModerationEngine(
    standards_profile="community-friendly",
    llm_provider="openai"  # or "anthropic"
)

# Analyze comments
comments = [
    "Great content, thanks for sharing!",
    "This is spam",
    "Love this! Can't wait for the next video!"
]

results = engine.analyze_comments(comments)
for comment, result in zip(comments, results):
    print(f"Comment: {comment}")
    print(f"  - Sentiment: {result.sentiment}")
    print(f"  - Violation: {result.violation_detected}")
    print(f"  - Action: {result.recommended_action}")
```

### For LLM Integration

If you're using this library with an LLM, refer to [docs/llm-context-guide.md](docs/llm-context-guide.md) for comprehensive guidance on how to leverage the context library.

## Project Structure

```
moderation-ai/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Technical architecture
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project configuration
│
├── docs/                              # Documentation for LLM consumption
│   ├── llm-context-guide.md          # How LLMs use this library
│   ├── standards-and-metrics.md      # Moderation standards
│   ├── api-reference/                # Platform API documentation
│   └── comment-analysis/             # Analysis methodology
│
├── platforms/                         # Platform-specific documentation
│   ├── twitter/                      # Twitter/X documentation
│   ├── reddit/                       # Reddit documentation
│   ├── instagram/                    # Instagram documentation
│   ├── medium/                       # Medium documentation
│   ├── youtube/                      # YouTube documentation
│   └── tiktok/                       # TikTok documentation
│
├── src/                               # Python source code
│   ├── core/                         # Core standards and metrics engine
│   ├── platforms/                    # Platform API integrations
│   ├── analysis/                     # Analysis modules
│   └── utils/                        # Utility functions
│
├── tests/                            # Test suite
├── examples/                         # Usage examples
└── .github/                          # GitHub configuration
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

## Documentation

### For Users
- **[LLM Context Guide](docs/llm-context-guide.md)** - How LLMs should use this library
- **[Standards & Metrics](docs/standards-and-metrics.md)** - Moderation standards and testable metrics
- **[API Reference](docs/api-reference/)** - Unified API documentation for all platforms

### For Developers
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and technical decisions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development workflow and contribution process
- **[Platform Documentation](platforms/)** - Platform-specific API guides and examples

### For Researchers
- **[Comment Analysis](docs/comment-analysis/)** - Methodology for comment analysis and categorization
- **[Implementation Phases](docs/implementation-phases.md)** - Detailed roadmap and design decisions

## Moderation Standards

This library implements a framework for defining and testing moderation standards:

### Standard Categories
- **Safety**: Harassment, threats, violence, abuse
- **Spam**: Promotional content, duplicate posts, bot activity
- **Quality**: Relevance, constructive feedback, conversation quality
- **Policy**: Platform-specific rules and guidelines
- **Tone**: Respectful communication, healthy discussions

### Standard Definition Format

Each standard includes:
- Clear definition and scope
- Testable criteria (metrics)
- Examples of violations
- Recommended actions
- Platform-specific variations

See [docs/standards-and-metrics.md](docs/standards-and-metrics.md) for complete standards definitions.

## Community Analysis Tools

The library includes tools for analyzing community feedback at scale:

### Capabilities
- **Summarization**: Condense large comment threads into key points
- **Categorization**: Automatically categorize comments by topic/sentiment
- **Sentiment Analysis**: Detect positive, negative, and neutral sentiment
- **FAQ Extraction**: Identify frequently asked questions
- **Trend Analysis**: Track how community sentiment changes over time
- **Idea Generation**: Suggest follow-up content based on community interest

## API Integration

Each platform has documented API integration patterns:

- **[Twitter API Guide](platforms/twitter/api-guide.md)**
- **[Reddit API Guide](platforms/reddit/api-guide.md)**
- **[Instagram API Guide](platforms/instagram/api-guide.md)**
- **[Medium API Guide](platforms/medium/api-guide.md)**
- **[YouTube API Guide](platforms/youtube/api-guide.md)**
- **[TikTok API Guide](platforms/tiktok/api-guide.md)**

Each guide includes:
- Authentication and setup
- Rate limiting strategies
- Data model specifications
- Code examples (conceptual)
- Error handling patterns

## Implementation Status

### Phase 0: Foundation ✅ In Progress
- [x] Project structure initialized
- [x] Core configuration files created
- [x] Directory structure established
- [ ] Foundation documentation complete
- [ ] GitHub issues created

### Phase 1: API Reference & Standards 📋 Planned
- API reference documentation
- Comment analysis framework

### Phase 2-4: Platform Documentation 📋 Planned
- Platform-specific guides and examples

### Phase 3: Core Python Library 📋 Planned
- Standards engine implementation
- Analysis modules
- Testing framework

### Phase 5-6: Platform Integrations 📋 Planned
- API client implementations
- Integration tests

### Phase 7: LLM Integration 📋 Planned
- LLM integration examples
- Production release (v1.0)

## Requirements

- **Python**: 3.9 or higher
- **Dependencies**: See [requirements.txt](requirements.txt)
- **API Keys**: Required for each platform (Twitter, Reddit, YouTube, etc.)

## Configuration

Create a `.env` file in the project root with your API credentials:

```env
# Twitter/X
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_token_secret

# Reddit
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_user_agent

# YouTube
YOUTUBE_API_KEY=your_key

# Other platforms...
```

See [docs/api-reference/authentication.md](docs/api-reference/authentication.md) for detailed setup instructions.

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/core/test_standards.py
```

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Coding standards
- Testing requirements
- Pull request process
- Adding new platforms
- Documentation guidelines

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/cgoss/Moderation-ai/issues)
- **Documentation**: [Full documentation](docs/)
- **Examples**: [Usage examples](examples/)

## Roadmap

See [docs/implementation-phases.md](docs/implementation-phases.md) for the detailed implementation roadmap including:
- Phase timeline and milestones
- Component breakdown
- Dependency mapping
- Success metrics

## Acknowledgments

This project is designed to work with Large Language Models like:
- OpenAI's GPT-4
- Anthropic's Claude
- Open-source models via local APIs

The documentation is optimized for LLM consumption and understanding.

## Authors

- **Colin Goss** - Initial concept and development

## Citation

If you use Moderation AI in your research or projects, please cite:

```bibtex
@software{moderation_ai_2024,
  title={Moderation AI: LLM Context Library for Content Moderation},
  author={Goss, Colin},
  year={2024},
  url={https://github.com/cgoss/Moderation-ai}
}
```

---

**Status**: Alpha (v0.1.0)
**Last Updated**: January 2024
**Maintainer**: Colin Goss
