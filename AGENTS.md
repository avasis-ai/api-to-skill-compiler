# AGENTS.md - API to Skill Compiler Project Context

This folder is home. Treat it that way.

## Project: API-to-Skill-Compiler (#75)

### Identity
- **Name**: API-to-Skill-Compiler
- **License**: Apache-2.0
- **Org**: avasis-ai
- **PyPI**: api-to-skill-compiler
- **Version**: 0.1.0
- **Tagline**: Instantly convert any REST API into an autonomous agent skill

### What It Does
Ingesting an OpenAPI/Swagger JSON file, this tool autonomously generates a highly optimized SKILL.md. It includes authentication handling, rate-limiting logic, and semantic descriptions dictating exactly when the agent should use each endpoint.

### Inspired By
- OpenAPI/Swagger
- Anthropic MCP
- LangChain
- Automation

### Core Components

#### `/ingestor/`
- OpenAPI/Swagger parsing
- Security scheme extraction
- Endpoint analysis

#### `/compiler/`
- SKILL.md generation
- Semantic mapping
- Template rendering

#### `/schemas/`
- OpenAPI schema validation
- SKILL.md schema definitions
- API documentation templates

### Technical Architecture

**Key Dependencies:**
- `click>=8.0` - CLI framework (Trust score: 8.8)
- `pyyaml>=6.0` - Configuration parsing (Trust score: 7.4)
- `jsonschema>=4.0` - Schema validation (Trust score: 10)

**Core Modules:**
1. `compiler.py` - Core compilation logic
2. `cli.py` - Command-line interface

### AI Coding Agent Guidelines

#### When Contributing:

1. **Understand the domain**: REST APIs are technical; agents need semantic understanding
2. **Use Context7**: Check trust scores for new libraries before adding dependencies
3. **Semantic mapping is key**: Translate technical API docs into natural language
4. **Security first**: Always document authentication requirements
5. **Best practices**: Include rate limiting, error handling, caching guidelines

#### What to Remember:

- **Semantic mapping**: Extract actions (get, create, update) and targets (users, orders, etc.)
- **Authentication**: Document all security schemes and requirements
- **Rate limiting**: Include best practices for respecting API limits
- **Error handling**: Document expected responses and error codes
- **Usage instructions**: Make endpoints self-documenting for agents

#### Common Patterns:

**Basic compilation:**
```python
from api_to_skill_compiler.compiler import OpenApiIngestor, SkillGenerator

# Ingest spec
ingester = OpenApiIngestor()
spec = ingester.ingest_spec("api-spec.json")

# Generate skill
generator = SkillGenerator(spec)
skill = generator.generate_skill(issue_number=1)
```

**Analyze API:**
```python
# Check API structure
print(f"Endpoints: {len(spec.endpoints)}")
print(f"Security: {list(spec.security_schemes.keys())}")
```

**Semantic mapping:**
```python
from api_to_skill_compiler.compiler import SemanticMapper

description = SemanticMapper.generate_semantic_description(endpoint)
instructions = SemanticMapper.generate_usage_instructions(endpoint)
```

### Project Status

- ✅ Initial implementation complete
- ✅ OpenAPI/Swagger parsing
- ✅ Semantic mapping engine
- ✅ SKILL.md generation
- ✅ Security documentation
- ✅ CLI interface
- ✅ Comprehensive test suite
- ⚠️ Real agent deployment pending
- ⚠️ Custom template support pending

### How to Work with This Project

1. **Read `SOUL.md`** - Understand who you are
2. **Read `USER.md`** - Know who you're helping
3. **Check `memory/YYYY-MM-DD.md`** - Recent context
4. **Read `MEMORY.md`** - Long-term decisions (main session only)
5. **Execute**: Code → Test → Commit

### Red Lines

- **No stubs or TODOs**: Every function must have real implementation
- **Type hints required**: All function signatures must include types
- **Docstrings mandatory**: Explain what, why, and how
- **Test coverage**: New features need tests
- **Security documentation**: Always document authentication requirements

### Development Workflow

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Format code
black src/ tests/
isort src/ tests/

# Check syntax
python -m py_compile src/api_to_skill_compiler/*.py

# Run CLI
api-to-skill --help

# Commit
git add -A && git commit -m "feat: add endpoint analysis"
```

### Key Files to Understand

- `src/api_to_skill_compiler/compiler.py` - Core compilation logic
- `src/api_to_skill_compiler/cli.py` - Command-line interface
- `tests/test_compiler.py` - Comprehensive test suite
- `README.md` - Usage examples and documentation

### Security Considerations

- **Authentication handling**: Always document security schemes
- **HTTPS requirement**: Emphasize secure connections
- **No secrets**: Never expose API keys or tokens
- **Trusted dependencies**: All verified via Context7
- **Apache 2.0**: Open source, community-driven

### Next Steps

1. Add more template variations (REST, GraphQL, etc.)
2. Build knowledge base of API patterns
3. Add support for custom semantic mappings
4. Create web interface for upload and generation
5. Add batch processing for multiple APIs
6. Integrate with agent deployment systems

### Unique Defensible Moat

The **complex semantic-mapping LLM pipeline** translates dry, technical API documentation into the highly specific, intention-based descriptions required for reliable agent tool-calling. The system understands:

- HTTP methods as actions (GET → retrieve, POST → create)
- Path parameters as resources
- Query parameters as filtering/criteria
- Request bodies as data structures
- Response codes as outcomes

This semantic understanding is what makes agents truly effective at using APIs autonomously.

---

**This file should evolve as you learn more about the project.**
