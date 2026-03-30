"""Tests for the compiler module."""

import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api_to_skill_compiler.compiler import (
    OpenApiIngestor,
    SkillGenerator,
    ApiSpec,
    ApiEndpoint,
    ApiParameter,
    HttpMethod,
    SemanticMapper
)


class TestApiParameter:
    """Tests for ApiParameter."""
    
    def test_api_parameter_to_dict(self):
        """Test converting parameter to dictionary."""
        param = ApiParameter(
            name="user_id",
            location="path",
            type="string",
            required=True,
            description="User identifier",
            schema={"type": "string", "format": "uuid"}
        )
        
        data = param.to_dict()
        
        assert data["name"] == "user_id"
        assert data["location"] == "path"
        assert data["required"] is True


class TestApiEndpoint:
    """Tests for ApiEndpoint."""
    
    def test_api_endpoint_to_dict(self):
        """Test converting endpoint to dictionary."""
        endpoint = ApiEndpoint(
            path="/users/{id}",
            method=HttpMethod.GET,
            operation_id="getUser",
            summary="Get user by ID",
            parameters=[
                ApiParameter(
                    name="id",
                    location="path",
                    type="string",
                    required=True,
                    description="User ID"
                )
            ],
            tags=["users"]
        )
        
        data = endpoint.to_dict()
        
        assert data["path"] == "/users/{id}"
        assert data["method"] == "GET"
        assert data["operation_id"] == "getUser"
        assert len(data["parameters"]) == 1


class TestApiSpec:
    """Tests for ApiSpec."""
    
    def test_api_spec_to_dict(self):
        """Test converting spec to dictionary."""
        spec = ApiSpec(
            name="TestAPI",
            version="1.0.0",
            description="Test API description",
            base_url="https://api.example.com",
            tags=["test", "api"]
        )
        
        data = spec.to_dict()
        
        assert data["name"] == "TestAPI"
        assert data["version"] == "1.0.0"
        assert data["tags"] == ["test", "api"]


class TestOpenApiIngestor:
    """Tests for OpenApiIngestor."""
    
    def test_ingest_with_minimal_spec(self):
        """Test ingesting minimal OpenAPI spec."""
        ingestor = OpenApiIngestor()
        
        spec_json = """
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/test": {
            "get": {
                "operationId": "getTest",
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        }
    }
}
"""
        spec = ingestor.ingest_from_string(spec_json)
        
        assert spec.name == "Test API"
        assert spec.version == "1.0.0"
        assert len(spec.endpoints) == 1
    
    def test_ingest_with_parameters(self):
        """Test ingesting spec with parameters."""
        ingestor = OpenApiIngestor()
        
        spec_json = """
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "paths": {
        "/users/{id}": {
            "get": {
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": true,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        }
    }
}
"""
        spec = ingestor.ingest_from_string(spec_json)
        
        assert len(spec.endpoints) == 1
        endpoint = spec.endpoints[0]
        assert len(endpoint.parameters) == 1
        assert endpoint.parameters[0].required is True
    
    def test_ingest_with_security_schemes(self):
        """Test ingesting spec with security schemes."""
        ingestor = OpenApiIngestor()
        
        spec_json = """
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0"
    },
    "components": {
        "securitySchemes": {
            "apiKey": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header"
            }
        }
    },
    "paths": {}
}
"""
        spec = ingestor.ingest_from_string(spec_json)
        
        assert "apiKey" in spec.security_schemes
        assert spec.security_schemes["apiKey"]["type"] == "apiKey"


class TestSemanticMapper:
    """Tests for SemanticMapper."""
    
    def test_generate_semantic_description(self):
        """Test generating semantic description."""
        endpoint = ApiEndpoint(
            path="/users",
            method=HttpMethod.GET,
            operation_id="getUsers",
            summary="List users",
            tags=["users"]
        )
        
        description = SemanticMapper.generate_semantic_description(endpoint)
        
        assert "List" in description
        assert "user" in description
    
    def test_extract_action_from_operation_id(self):
        """Test action extraction from operation_id."""
        endpoint = ApiEndpoint(
            path="/users",
            method=HttpMethod.GET,
            operation_id="searchUsers"
        )
        
        description = SemanticMapper.generate_semantic_description(endpoint)
        
        assert "search" in description or "Search" in description
    
    def test_extract_target_from_path(self):
        """Test target extraction from path."""
        endpoint = ApiEndpoint(
            path="/orders/{id}/items",
            method=HttpMethod.GET
        )
        
        description = SemanticMapper.generate_semantic_description(endpoint)
        
        assert "item" in description or "items" in description


class TestSkillGenerator:
    """Tests for SkillGenerator."""
    
    def test_generate_skill_basic(self):
        """Test generating basic skill."""
        spec = ApiSpec(
            name="TestAPI",
            version="1.0.0",
            description="Test API",
            base_url="https://api.example.com"
        )
        
        generator = SkillGenerator(spec)
        skill = generator.generate_skill(1)
        
        assert "# TestAPI" in skill
        assert "## Tagline" in skill
        assert "## What It Does" in skill
    
    def test_generate_skill_with_endpoints(self):
        """Test generating skill with endpoints."""
        spec = ApiSpec(
            name="TestAPI",
            version="1.0.0",
            description="Test API",
            base_url="https://api.example.com",
            endpoints=[
                ApiEndpoint(
                    path="/users",
                    method=HttpMethod.GET,
                    operation_id="getUsers",
                    summary="List users"
                )
            ]
        )
        
        generator = SkillGenerator(spec)
        skill = generator.generate_skill(1)
        
        assert "GET /users" in skill
        assert "List users" in skill
    
    def test_generate_skill_with_metadata(self):
        """Test generating skill with metadata."""
        spec = ApiSpec(
            name="TestAPI",
            version="1.0.0",
            description="Test API",
            base_url="https://api.example.com",
            tags=["users", "api"]
        )
        
        generator = SkillGenerator(spec)
        skill = generator.generate_skill(1)
        
        assert "### Metadata" in skill
        assert "TestAPI" in skill
        assert "1.0.0" in skill


class TestIntegration:
    """Integration tests."""
    
    def test_full_compilation_workflow(self):
        """Test complete compilation workflow."""
        ingestor = OpenApiIngestor()
        
        spec_json = """
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0",
        "description": "A test API for skill generation"
    },
    "servers": [
        {"url": "https://api.example.com"}
    ],
    "components": {
        "securitySchemes": {
            "apiKey": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header"
            }
        }
    },
    "paths": {
        "/users": {
            "get": {
                "operationId": "getUsers",
                "summary": "List all users",
                "tags": ["users"],
                "responses": {
                    "200": {"description": "Successful response"}
                }
            },
            "post": {
                "operationId": "createUser",
                "summary": "Create a user",
                "tags": ["users"],
                "requestBody": {
                    "required": true,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "User created"}
                }
            }
        },
        "/users/{id}": {
            "get": {
                "operationId": "getUser",
                "summary": "Get user by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": true,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "User found"},
                    "404": {"description": "User not found"}
                }
            }
        }
    }
}
"""
        # Ingest spec
        spec = ingestor.ingest_from_string(spec_json)
        
        # Verify ingestion
        assert spec.name == "Test API"
        assert spec.version == "1.0.0"
        assert len(spec.endpoints) == 3
        assert "apiKey" in spec.security_schemes
        
        # Generate skill
        generator = SkillGenerator(spec)
        skill = generator.generate_skill(42)
        
        # Verify generation
        assert "# Test API (#42)" in skill
        assert "List all users" in skill
        assert "Create a user" in skill
        assert "Get user by ID" in skill
        assert "apiKey" in skill
        assert "security" in skill.lower()
        
        # Verify API info
        api_info = generator.get_api_info()
        assert api_info["name"] == "Test API"
        assert api_info["endpoint_count"] == 3
        assert api_info["has_security"] is True
