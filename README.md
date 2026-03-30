# README.md - API to Skill Compiler

## Instantly Convert Any REST API into an Autonomous Agent Skill

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/api-to-skill-compiler.svg)](https://pypi.org/project/api-to-skill-compiler/)

**API to Skill Compiler** transforms REST API specifications into optimized SKILL.md files for autonomous agents. Simply provide an OpenAPI/Swagger JSON file, and it generates a complete agent skill with authentication handling, rate-limiting logic, and semantic descriptions.

## 🎯 What It Does

- **OpenAPI/Swagger Ingestion**: Parse any REST API specification
- **Semantic Mapping**: Translate technical API docs into agent-friendly descriptions
- **Security Handling**: Automatically extract and document authentication requirements
- **Rate Limiting**: Include best practices for handling API limits
- **Endpoint Documentation**: Generate comprehensive endpoint descriptions with usage instructions
- **Error Handling**: Document expected responses and error codes

### Example Use Case

```python
from api_to_skill_compiler.compiler import OpenApiIngestor, SkillGenerator

# Ingest OpenAPI spec
ingester = OpenApiIngestor()
api_spec = ingester.ingest_spec("api-spec.json")

# Generate SKILL.md
generator = SkillGenerator(api_spec)
skill_content = generator.generate_skill(issue_number=1)

# Save to file
with open("SKILL_API.md", "w") as f:
    f.write(skill_content)
```

## 🚀 Features

- **Smart Semantic Mapping**: Understands API semantics to generate natural language descriptions
- **Comprehensive Documentation**: Includes all endpoints, parameters, and security requirements
- **Best Practices Integration**: Embeds rate limiting, error handling, and caching guidelines
- **Flexible Templates**: Customizable SKILL.md templates for different use cases
- **CLI Interface**: Command-line tools for compilation and analysis

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAPI/Swagger specification file

### Install from PyPI

```bash
pip install api-to-skill-compiler
```

### Install from Source

```bash
git clone https://github.com/avasis-ai/api-to-skill-compiler.git
cd api-to-skill-compiler
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
pip install pytest pytest-mock black isort
```

## 🔧 Usage

### Command-Line Interface

```bash
# Check version
api-to-skill --version

# Compile an OpenAPI spec to SKILL.md
api-to-skill compile spec.json --output SKILL_API.md

# Analyze an API specification
api-to-skill analyze spec.json

# View authentication samples
api-to-skill samples --sample api_key
```

### Programmatic Usage

```python
from api_to_skill_compiler.compiler import OpenApiIngestor, SkillGenerator

# Load and parse API specification
ingester = OpenApiIngestor()
spec = ingester.ingest_spec("api-spec.json")

# Verify parsing
print(f"API: {spec.name} v{spec.version}")
print(f"Endpoints: {len(spec.endpoints)}")
print(f"Security: {list(spec.security_schemes.keys())}")

# Generate SKILL.md with issue reference
generator = SkillGenerator(spec)
skill_md = generator.generate_skill(issue_number=42)

# Access API metadata
api_info = generator.get_api_info()
print(f"API Info: {api_info}")
```

### Example OpenAPI Specification

Create `api-spec.json`:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Payment API",
    "version": "1.0.0",
    "description": "Process payments and manage transactions"
  },
  "servers": [
    {"url": "https://api.payments.example.com"}
  ],
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    }
  },
  "paths": {
    "/payments": {
      "post": {
        "operationId": "createPayment",
        "summary": "Create a new payment",
        "tags": ["payments"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "amount": {"type": "number"},
                  "currency": {"type": "string"}
                }
              }
            }
          }
        },
        "responses": {
          "201": {"description": "Payment created"},
          "400": {"description": "Invalid request"}
        }
      }
    }
  }
}
```

Compile it:

```bash
api-to-skill compile api-spec.json -o SKILL_PAYMENT.md
```

## 📚 API Reference

### OpenApiIngestor

Parses OpenAPI/Swagger specifications.

#### `ingest_spec(spec_path)` → ApiSpec

Ingest specification from file.

#### `ingest_from_string(spec_string)` → ApiSpec

Ingest specification from JSON string.

### SkillGenerator

Generates SKILL.md files.

#### `generate_skill(issue_number)` → str

Generate complete SKILL.md content.

#### `get_api_info()` → Dict

Get API metadata information.

### SemanticMapper

Maps API semantics to agent-friendly descriptions.

#### `generate_semantic_description(endpoint)` → str

Generate natural language description.

#### `generate_usage_instructions(endpoint)` → str

Generate usage instructions.

## 🧪 Testing

Run tests with pytest:

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
api-to-skill-compiler/
├── README.md
├── pyproject.toml
├── LICENSE
├── src/
│   └── api_to_skill_compiler/
│       ├── __init__.py
│       ├── compiler.py
│       └── cli.py
├── tests/
│   └── test_compiler.py
└── .github/
    └── ISSUE_TEMPLATE/
        └── bug_report.md
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `python -m pytest tests/ -v`
5. **Submit a pull request**

### Development Setup

```bash
git clone https://github.com/avasis-ai/api-to-skill-compiler.git
cd api-to-skill-compiler
pip install -e ".[dev]"
pre-commit install
```

## 📝 License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

## 🎯 Vision

API to Skill Compiler democratizes agent creation by:

- **Instant integration**: Convert any REST API to an agent in seconds
- **Semantic understanding**: Agents understand what APIs do, not just how to call them
- **Security best practices**: Automatic authentication and rate limiting handling
- **Developer efficiency**: Save hours of manual documentation and configuration

## 🌟 Impact

This tool enables:

- **Rapid agent development**: Create agents for existing APIs instantly
- **Consistent quality**: Standardized skill generation across all APIs
- **Better agents**: Semantic understanding leads to better agent behavior
- **API ecosystem expansion**: Connect millions of APIs to the agent ecosystem

## 🛡️ Security & Trust

- **Trusted dependencies**: PyYAML (7.4), click (8.8), jsonschema (10) - [Context7 verified](https://context7.com)
- **Apache 2.0**: Open source, community-driven
- **No external API calls**: All processing local

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/avasis-ai/api-to-skill-compiler/wiki)
- **Issues**: [GitHub Issues](https://github.com/avasis-ai/api-to-skill-compiler/issues)

## 🙏 Acknowledgments

- **OpenAPI Initiative**: For the OpenAPI specification
- **Anthropic MCP**: Inspiration for tool integration
- **LangChain**: Tool design patterns
- **Developer community**: Shared knowledge and best practices

---

**Made with ❤️ by [Avasis AI](https://avasis.ai)**

*The ultimate developer convenience tool. Bridge Web 2.0 APIs to Web 3.0 agents.*
