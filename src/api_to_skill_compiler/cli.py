"""CLI for API to Skill Compiler."""

import click
import sys
import os
from pathlib import Path

from .compiler import (
    OpenApiIngestor,
    SkillGenerator,
    ApiSpec,
    SemanticMapper
)


@click.group()
@click.version_option(version="0.1.0", prog_name="api-to-skill")
def main():
    """API to Skill Compiler - Convert REST APIs to agent skills."""
    pass


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='SKILL_API.md',
              help='Output SKILL.md file path')
@click.option('--issue-number', '-i', default=1,
              help='Issue number for reference')
def compile(input_path: str, output: str, issue_number: int) -> None:
    """Compile an OpenAPI specification to a SKILL.md file."""
    try:
        click.echo(f"📥 Reading specification: {input_path}")
        
        # Ingest specification
        ingestor = OpenApiIngestor()
        spec = ingestor.ingest_spec(input_path)
        
        click.echo(f"✅ Parsed API: {spec.name} v{spec.version}")
        click.echo(f"📊 Found {len(spec.endpoints)} endpoints")
        
        # Generate skill
        generator = SkillGenerator(spec)
        skill_content = generator.generate_skill(issue_number)
        
        # Write output
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(skill_content)
        
        click.echo(f"📝 Generated: {output}")
        
        # Print API info
        api_info = generator.get_api_info()
        click.echo(f"\nAPI Info:")
        click.echo(f"  Name: {api_info['name']}")
        click.echo(f"  Version: {api_info['version']}")
        click.echo(f"  Endpoints: {api_info['endpoint_count']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('input_path', type=click.Path(exists=True))
def analyze(input_path: str) -> None:
    """Analyze an OpenAPI specification."""
    try:
        click.echo(f"📥 Analyzing: {input_path}")
        
        # Ingest specification
        ingestor = OpenApiIngestor()
        spec = ingestor.ingest_spec(input_path)
        
        click.echo(f"\n📊 API Analysis: {spec.name} v{spec.version}")
        click.echo(f"📍 Base URL: {spec.base_url}")
        click.echo(f"📝 Endpoints: {len(spec.endpoints)}")
        
        if spec.tags:
            click.echo(f"\n🏷️ Tags: {', '.join(spec.tags)}")
        
        if spec.security_schemes:
            click.echo(f"\n🔒 Security schemes:")
            for scheme in spec.security_schemes:
                click.echo(f"  - {scheme}")
        
        # Sample endpoint analysis
        if spec.endpoints:
            click.echo(f"\n📋 Sample Endpoints:")
            for endpoint in spec.endpoints[:3]:
                semantic_desc = SemanticMapper.generate_semantic_description(endpoint)
                click.echo(f"  {endpoint.method.value} {endpoint.path}")
                click.echo(f"    → {semantic_desc}")
        
        if len(spec.endpoints) > 3:
            click.echo(f"\n  ... and {len(spec.endpoints) - 3} more endpoints")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--sample', '-s', type=click.Choice(['api_key', 'oauth2', 'bearer']),
              default='api_key',
              help='Sample security scheme to demonstrate')
def samples(sample: str) -> None:
    """Display sample security configurations."""
    
    samples = {
        "api_key": """
# API Key Authentication
x-api-key: YOUR_API_KEY
""".strip(),
        "oauth2": """
# OAuth2 Authentication
Authorization: Bearer YOUR_ACCESS_TOKEN
""".strip(),
        "bearer": """
# Bearer Token
Authorization: Bearer YOUR_JWT_TOKEN
""".strip()
    }
    
    click.echo(f"🔐 {sample.upper()} Authentication Sample:")
    click.echo(samples[sample])


if __name__ == '__main__':
    main()
