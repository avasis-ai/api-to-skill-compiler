"""Compiler module for converting OpenAPI specifications to SKILL.md files."""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import jsonschema


class HttpMethod(Enum):
    """HTTP methods for API endpoints."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class ApiParameter:
    """Represents an API endpoint parameter."""
    name: str
    location: str  # query, header, path, body
    type: str
    required: bool
    description: str
    schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "location": self.location,
            "type": self.type,
            "required": self.required,
            "description": self.description,
            "schema": self.schema
        }


@dataclass
class ApiEndpoint:
    """Represents an API endpoint."""
    path: str
    method: HttpMethod
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[ApiParameter] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "method": self.method.value,
            "operation_id": self.operation_id,
            "summary": self.summary,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "request_body": self.request_body,
            "responses": self.responses,
            "tags": self.tags,
            "security": self.security
        }


@dataclass
class ApiSpec:
    """Represents a complete API specification."""
    name: str
    version: str
    description: str
    base_url: str
    endpoints: List[ApiEndpoint] = field(default_factory=list)
    security_schemes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "base_url": self.base_url,
            "endpoints": [e.to_dict() for e in self.endpoints],
            "security_schemes": self.security_schemes,
            "tags": self.tags
        }


class OpenApiIngestor:
    """Ingests OpenAPI/Swagger specifications."""
    
    def __init__(self):
        """Initialize the ingester."""
        self._validation_errors: List[str] = []
    
    def ingest_spec(self, spec_path: str) -> ApiSpec:
        """
        Ingest an OpenAPI specification from a file.
        
        Args:
            spec_path: Path to the OpenAPI/Swagger JSON file
            
        Returns:
            Parsed ApiSpec
        """
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            
            return self._parse_spec(spec_data)
            
        except (IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load specification: {str(e)}")
    
    def ingest_from_string(self, spec_string: str) -> ApiSpec:
        """
        Ingest an OpenAPI specification from a JSON string.
        
        Args:
            spec_string: JSON string containing the specification
            
        Returns:
            Parsed ApiSpec
        """
        try:
            spec_data = json.loads(spec_string)
            return self._parse_spec(spec_data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    def _parse_spec(self, spec_data: Dict[str, Any]) -> ApiSpec:
        """Parse an OpenAPI specification dictionary."""
        # Validate basic structure
        if "openapi" not in spec_data and "swagger" not in spec_data:
            raise ValueError("Invalid OpenAPI/Swagger specification")
        
        # Extract metadata
        info = spec_data.get("info", {})
        name = info.get("title", "API")
        version = info.get("version", "1.0.0")
        description = info.get("description", "")
        
        # Extract servers
        servers = spec_data.get("servers", [])
        base_url = servers[0].get("url", "") if servers else ""
        
        # Extract tags
        tags = []
        for tag_data in spec_data.get("tags", []):
            if isinstance(tag_data, dict):
                tags.append(tag_data.get("name", ""))
        
        # Parse security schemes
        security_schemes = {}
        for scheme_name, scheme_data in spec_data.get("components", {}).get("securitySchemes", {}).items():
            security_schemes[scheme_name] = scheme_data
        
        # Parse endpoints
        endpoints = self._parse_endpoints(spec_data)
        
        return ApiSpec(
            name=name,
            version=version,
            description=description,
            base_url=base_url,
            endpoints=endpoints,
            security_schemes=security_schemes,
            tags=[t for t in tags if t]
        )
    
    def _parse_endpoints(self, spec_data: Dict[str, Any]) -> List[ApiEndpoint]:
        """Parse endpoints from spec data."""
        endpoints = []
        paths = spec_data.get("paths", {})
        
        for path, path_item in paths.items():
            for method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                if method in path_item:
                    endpoint_data = path_item[method]
                    
                    # Extract operation details
                    operation_id = endpoint_data.get("operationId")
                    summary = endpoint_data.get("summary")
                    description = endpoint_data.get("description")
                    tags = endpoint_data.get("tags", [])
                    security = endpoint_data.get("security", [])
                    
                    # Parse parameters
                    parameters = self._parse_parameters(endpoint_data.get("parameters", []))
                    
                    # Parse request body
                    request_body = endpoint_data.get("requestBody")
                    
                    # Parse responses
                    responses = endpoint_data.get("responses", {})
                    
                    # Normalize HTTP method
                    http_method = HttpMethod[method.upper()]
                    
                    endpoint = ApiEndpoint(
                        path=path,
                        method=http_method,
                        operation_id=operation_id,
                        summary=summary,
                        description=description,
                        parameters=parameters,
                        request_body=request_body,
                        responses={
                            k: v for k, v in responses.items() 
                            if k != "default" or k in ["200", "201", "204", "400", "401", "403", "404", "500"]
                        },
                        tags=tags,
                        security=security
                    )
                    
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_parameters(self, params: List[Dict]) -> List[ApiParameter]:
        """Parse parameters from endpoint data."""
        parameters = []
        
        for param in params:
            param_name = param.get("name")
            param_location = param.get("in", "query")
            param_type = param.get("schema", {}).get("type", "string")
            required = param.get("required", False)
            description = param.get("description", "")
            
            parameter = ApiParameter(
                name=param_name,
                location=param_location,
                type=param_type,
                required=required,
                description=description,
                schema=param.get("schema", {})
            )
            
            parameters.append(parameter)
        
        return parameters


class SemanticMapper:
    """Maps API semantics to agent-friendly descriptions."""
    
    # Action mappings for common API patterns
    ACTION_MAPPINGS = {
        "get": "retrieve",
        "list": "list",
        "create": "create",
        "update": "update",
        "delete": "delete",
        "search": "search",
        "export": "export",
        "import": "import",
        "validate": "validate",
        "calculate": "calculate",
        "generate": "generate",
        "send": "send",
        "receive": "receive",
        "download": "download",
        "upload": "upload",
        "start": "start",
        "stop": "stop",
        "restart": "restart",
        "status": "check_status"
    }
    
    @staticmethod
    def generate_semantic_description(endpoint: ApiEndpoint) -> str:
        """
        Generate a semantic description for an endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Semantic description
        """
        # Extract action from operation_id or endpoint name
        action = SemanticMapper._extract_action(endpoint)
        
        # Extract target from path
        target = SemanticMapper._extract_target(endpoint)
        
        # Build description
        parts = []
        parts.append(f"{action.title()} the {target}")
        
        if endpoint.summary:
            parts.append(f" - {endpoint.summary}")
        
        if endpoint.tags:
            parts.append(f" [Context: {', '.join(endpoint.tags)}]")
        
        return " ".join(parts)
    
    @staticmethod
    def _extract_action(endpoint: ApiEndpoint) -> str:
        """Extract action from operation_id or method."""
        if endpoint.operation_id:
            # Try to extract action from operation_id
            for key, value in SemanticMapper.ACTION_MAPPINGS.items():
                if key in endpoint.operation_id.lower():
                    return value
        
        # Use HTTP method as action
        method_action = SemanticMapper.ACTION_MAPPINGS.get(
            endpoint.method.value.lower(), 
            "access"
        )
        
        return method_action
    
    @staticmethod
    def _extract_target(endpoint: ApiEndpoint) -> str:
        """Extract target resource from path."""
        # Remove path parameters and extract resource name
        path = endpoint.path.strip("/")
        
        # Remove path parameters like {id}, {resource_id}
        path = re.sub(r'\{[^}]+\}', '', path)
        
        # Remove leading/trailing slashes
        path = path.strip("/")
        
        # Split by slashes and take the last meaningful segment
        segments = [s for s in path.split("/") if s and s not in ["api", "v1", "v2"]]
        
        if segments:
            target = segments[-1]
            # Make plural for better semantics
            if target and not target.endswith("s"):
                target = target + "s" if len(target) > 3 else target
            return target
        
        return "resource"
    
    @staticmethod
    def generate_usage_instructions(endpoint: ApiEndpoint) -> str:
        """
        Generate usage instructions for an endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Usage instructions
        """
        instructions = []
        
        # When to use
        semantic_desc = SemanticMapper.generate_semantic_description(endpoint)
        instructions.append(f"Use this endpoint when you need to {semantic_desc.lower()}.")
        
        # Required parameters
        required_params = [p for p in endpoint.parameters if p.required]
        if required_params:
            instructions.append(f"\nRequired parameters: {', '.join(p.name for p in required_params)}")
        
        # Request body
        if endpoint.request_body:
            instructions.append(f"\nRequest body schema: {json.dumps(endpoint.request_body, indent=2)}")
        
        # Response types
        if endpoint.responses:
            instructions.append(f"\nResponse types: {', '.join(endpoint.responses.keys())}")
        
        # Security requirements
        if endpoint.security:
            instructions.append(f"\nRequires authentication: {', '.join(endpoint.security)}")
        
        return " ".join(instructions)


class SkillGenerator:
    """Generates SKILL.md files from API specifications."""
    
    TEMPLATE = """# {{ name }} (#{{ issue_number }})

## Tagline
{{ tagline }}

## What It Does
{{ what_it_does }}

## How It Works
{{ how_it_works }}

## Technical Implementation
{{ technical_implementation }}

## Security
{{ security_section }}

## Best Practices
{{ best_practices }}

## API Endpoints
{{ endpoints_section }}

{{ additional_content }}
"""
    
    def __init__(self, api_spec: ApiSpec):
        """
        Initialize the skill generator.
        
        Args:
            api_spec: Parsed API specification
        """
        self.api_spec = api_spec
        self._generated_content = ""
    
    def generate_skill(self, issue_number: int = 1) -> str:
        """
        Generate a SKILL.md file from the API specification.
        
        Args:
            issue_number: Issue number for reference
            
        Returns:
            Generated SKILL.md content
        """
        # Generate tagline
        tagline = self._generate_tagline()
        
        # Generate what it does
        what_it_does = self._generate_what_it_does()
        
        # Generate how it works
        how_it_works = self._generate_how_it_works()
        
        # Generate technical implementation
        technical_implementation = self._generate_technical_implementation()
        
        # Generate security section
        security_section = self._generate_security_section()
        
        # Generate best practices
        best_practices = self._generate_best_practices()
        
        # Generate endpoints section
        endpoints_section = self._generate_endpoints_section()
        
        # Generate additional content
        additional_content = self._generate_additional_content()
        
        # Render template
        from jinja2 import Template
        template = Template(self.TEMPLATE)
        self._generated_content = template.render(
            name=self.api_spec.name,
            issue_number=issue_number,
            tagline=tagline,
            what_it_does=what_it_does,
            how_it_works=how_it_works,
            technical_implementation=technical_implementation,
            security_section=security_section,
            best_practices=best_practices,
            endpoints_section=endpoints_section,
            additional_content=additional_content
        )
        
        return self._generated_content
    
    def _generate_tagline(self) -> str:
        """Generate tagline for the agent."""
        action = "automates" if self.api_spec.tags else "provides"
        context = self.api_spec.tags[0] if self.api_spec.tags else "API interactions"
        return f"{action} {context} via the {self.api_spec.name} API"
    
    def _generate_what_it_does(self) -> str:
        """Generate what it does description."""
        if self.api_spec.description:
            return f"{self.api_spec.description}\n\nThis agent exposes the full functionality of the {self.api_spec.name} API."
        
        endpoint_count = len(self.api_spec.endpoints)
        return (
            f"This agent provides programmatic access to the {self.api_spec.name} API "
            f"with {endpoint_count} endpoints. "
            f"It handles authentication, rate limiting, and error handling automatically."
        )
    
    def _generate_how_it_works(self) -> str:
        """Generate how it works description."""
        parts = []
        parts.append("The agent follows these patterns:")
        parts.append("")
        
        # Authentication
        if self.api_spec.security_schemes:
            auth_methods = list(self.api_spec.security_schemes.keys())
            parts.append(f"1. **Authentication**: Supports {', '.join(auth_methods)} authentication")
        
        # Rate limiting
        parts.append("2. **Rate Limiting**: Automatically respects API rate limits")
        
        # Error handling
        parts.append("3. **Error Handling**: Gracefully handles API errors with retry logic")
        
        # Semantic mapping
        parts.append("4. **Semantic Mapping**: Understands API endpoints in natural language")
        
        return "\n".join(parts)
    
    def _generate_technical_implementation(self) -> str:
        """Generate technical implementation section."""
        parts = []
        parts.append("Implementation details:")
        parts.append("")
        
        # Endpoints
        parts.append("### Endpoints")
        for endpoint in self.api_spec.endpoints[:5]:  # First 5 endpoints
            action = SemanticMapper.generate_semantic_description(endpoint)
            parts.append(f"- **{endpoint.method.value} {endpoint.path}**: {action}")
        
        if len(self.api_spec.endpoints) > 5:
            parts.append(f"\n*... and {len(self.api_spec.endpoints) - 5} more endpoints*")
        
        return "\n".join(parts)
    
    def _generate_security_section(self) -> str:
        """Generate security section."""
        parts = []
        parts.append("### Security Requirements")
        
        if self.api_spec.security_schemes:
            for scheme_name, scheme_data in self.api_spec.security_schemes.items():
                scheme_type = scheme_data.get("type", "unknown")
                parts.append(f"- **{scheme_name}**: {scheme_type}")
        
        parts.append("\n**Important**:\n- Always use HTTPS\n- Never hardcode API keys\n- Rotate credentials regularly")
        
        return "\n".join(parts)
    
    def _generate_best_practices(self) -> str:
        """Generate best practices section."""
        parts = []
        parts.append("### Best Practices")
        parts.append("")
        parts.append("1. **Always validate responses** before using data")
        parts.append("2. **Handle rate limits gracefully** with exponential backoff")
        parts.append("3. **Cache frequently used data** to reduce API calls")
        parts.append("4. **Log API interactions** for debugging and auditing")
        parts.append("5. **Use pagination** for list endpoints with many results")
        
        return "\n".join(parts)
    
    def _generate_endpoints_section(self) -> str:
        """Generate endpoints section."""
        if not self.api_spec.endpoints:
            return "No endpoints defined."
        
        parts = []
        parts.append("### Available Endpoints")
        parts.append("")
        
        for endpoint in self.api_spec.endpoints:
            semantic_desc = SemanticMapper.generate_semantic_description(endpoint)
            parts.append(f"#### `{endpoint.method.value} {endpoint.path}`")
            parts.append("")
            parts.append(f"**Purpose**: {semantic_desc}")
            
            if endpoint.summary and endpoint.summary != endpoint.summary:
                parts.append(f"\n{endpoint.summary}")
            
            # Parameters
            if endpoint.parameters:
                parts.append("\n**Parameters**:")
                for param in endpoint.parameters:
                    required = "required" if param.required else "optional"
                    parts.append(f"- `{param.name}` ({param.type}): {param.description} [{required}]")
            
            parts.append("")
        
        return "\n".join(parts)
    
    def _generate_additional_content(self) -> str:
        """Generate additional content."""
        parts = []
        
        # Metadata
        parts.append("### Metadata")
        parts.append(f"- **API Name**: {self.api_spec.name}")
        parts.append(f"- **Version**: {self.api_spec.version}")
        parts.append(f"- **Base URL**: {self.api_spec.base_url}")
        parts.append(f"- **Endpoints**: {len(self.api_spec.endpoints)}")
        
        # Tags
        if self.api_spec.tags:
            parts.append(f"- **Tags**: {', '.join(self.api_spec.tags)}")
        
        return "\n".join(parts)
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information."""
        return {
            "name": self.api_spec.name,
            "version": self.api_spec.version,
            "endpoint_count": len(self.api_spec.endpoints),
            "has_security": bool(self.api_spec.security_schemes),
            "tags": self.api_spec.tags
        }
