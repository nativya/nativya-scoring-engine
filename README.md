# Nativya Scoring Engine

A decentralized AI scoring engine designed to run in Trusted Execution Environments (TEE) for secure, privacy-preserving evaluation of conversational AI data. Nativya provides comprehensive quality, uniqueness, and integrity scoring for AI-generated content in a trustless, decentralized manner.

## 🌟 Features

- **TEE-Native**: Designed specifically for Trusted Execution Environments
- **AI Quality Scoring**: Advanced NLP-based quality assessment using sentence transformers
- **Uniqueness Detection**: SimHash-based duplicate detection and uniqueness scoring
- **Privacy-First**: PII scrubbing and secure data processing
- **Two-Tier Architecture**: Local proof generation + global integrity verification
- **Containerized**: Docker-ready for easy deployment
- ** Comprehensive Metrics**: Quality, uniqueness, complexity, and word count scoring
- **API Integration**: RESTful API for frontend integration

## 🏛️ Architecture

Nativya implements a sophisticated two-tier scoring architecture:

### Tier 1: Local Data Proof (`my_proof/`)

- **Quality Assessment**: Semantic similarity analysis between user prompts and AI responses
- **Uniqueness Hashing**: SimHash fingerprint generation for content deduplication
- **PII Protection**: Automatic detection and filtering of personally identifiable information
- **Complexity Analysis**: Lexical diversity and linguistic complexity scoring

### Tier 2: Global Integrity Service (`orchestrator.py`)

- **Global Uniqueness**: Cross-dataset uniqueness verification via external API
- **Score Aggregation**: Weighted combination of local and global metrics
- **Integrity Validation**: End-to-end proof verification

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- 4GB+ RAM (for ML models)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/nativya-scoring-engine.git
   cd nativya-scoring-engine
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python -m nltk.downloader punkt
   ```

3. **Configure environment**
   ```bash
   cp my_proof/.env.example my_proof/.env
   # Edit .env with your configuration
   ```

### Usage

#### Direct Execution

```bash
# Process data from file
python -m my_proof

# Process data from stdin (TEE mode)
echo '{"conversations": [...], "uniqueness_hashes": [...]}' | python -m my_proof
```

#### Docker Deployment

```bash
# Build the image
docker build -t nativya-scoring-engine .

# Run with volume mounts
docker run --rm \
  -v $(pwd)/input:/input \
  -v $(pwd)/output:/output \
  nativya-scoring-engine
```

#### Full Orchestration

```bash
# Run complete two-tier validation
python orchestrator.py input/data.json
```

## 📊 Input Format

### Conversation Data

```json
{
  "conversations": [
    {
      "user": "What is machine learning?",
      "bot": "Machine learning is a subset of artificial intelligence..."
    }
  ],
  "uniqueness_hashes": ["12345678901234567890"]
}
```

### TEE Request Format

```json
{
  "job_id": "job_123",
  "file_id": "file_456",
  "nonce": "random_nonce",
  "conversations": [
    {
      "prompt": "User question",
      "answer": "AI response"
    }
  ],
  "uniqueness_hashes": ["hash1", "hash2"]
}
```

## 📈 Output Format

```json
{
  "dlp_id": 0,
  "valid": true,
  "score": 0.85,
  "quality": 0.78,
  "uniqueness": 0.92,
  "attributes": {
    "total_conversations": 10,
    "valid_conversations": 9,
    "average_complexity": 0.65,
    "valid_fingerprints": ["hash1", "hash2"]
  },
  "metadata": {
    "model_version": "1.0",
    "processing_time": 2.34
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable                     | Description                          | Default            |
| ---------------------------- | ------------------------------------ | ------------------ |
| `USER_EMAIL`                 | User identifier for scoring          | `None`             |
| `TIER_2_API_KEY`             | API key for global integrity service | Required           |
| `SENTENCE_TRANSFORMER_MODEL` | Model for semantic analysis          | `all-MiniLM-L6-v2` |
| `TARGET_WORD_COUNT`          | Target word count for scoring        | `100`              |

### Scoring Weights

Configure in `orchestrator.py`:

- **Quality Weight**: 0.6 (60%)
- **Global Uniqueness Weight**: 0.4 (40%)

## 🛠️ Development

### Project Structure

```
nativya-scoring-engine/
├── my_proof/                 # Core scoring engine
│   ├── models/              # Data models
│   ├── __main__.py          # Entry point
│   ├── proof.py             # Main proof logic
│   ├── scorer.py            # Scoring algorithms
│   ├── config.py            # Configuration
│   └── models_llm.py        # LLM-specific models
├── input/                   # Input data directory
├── orchestrator.py          # Two-tier orchestration
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=my_proof
```

### Code Quality

```bash
# Format code
black my_proof/
isort my_proof/

# Lint code
flake8 my_proof/
mypy my_proof/
```

## 🔒 Security & Privacy

- **PII Protection**: Automatic detection and filtering of emails, phone numbers
- **TEE Compatibility**: Designed for secure execution in trusted environments
- **Data Isolation**: No persistent storage of sensitive data
- **Secure Communication**: HTTPS-only external API calls

## 🌐 TEE Integration

Nativya is optimized for Trusted Execution Environment deployment:

- **Stdin/Stdout Interface**: Clean I/O for TEE orchestration
- **Stateless Processing**: No persistent state between runs
- **Resource Efficient**: Optimized for constrained TEE environments
- **Verifiable Outputs**: Cryptographically verifiable proof generation

## 📋 API Reference

### Scoring Metrics

- **Quality Score**: Semantic similarity between prompts and responses (0-1)
- **Uniqueness Score**: Content uniqueness based on SimHash (0-1)
- **Complexity Score**: Lexical diversity and linguistic complexity (0-1)
- **Word Count Score**: Normalized word count assessment (0-1)

### Error Handling

The system provides detailed error reporting:

- Invalid input format
- Missing required fields
- PII detection failures
- Model loading errors

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for public methods
- Write tests for new features
- Maintain backwards compatibility
