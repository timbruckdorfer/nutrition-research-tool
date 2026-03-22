"""
Nutrition Research Paper Analyzer - MCP Server

This is an MCP (Model Context Protocol) server that provides tools for analyzing
scientific papers in the nutrition/health sector.

What is an MCP Server?
- A process that exposes "tools" (functions) to MCP clients
- Uses JSON-RPC protocol over stdio (standard input/output)
- Clients can discover and call these tools
- Similar to REST APIs, but for AI agents

Architecture:
    MCP Client (FastAPI) <--stdin/stdout--> MCP Server (this file)
                                                    |
                                                    v
                                            Tool implementations
"""

import asyncio
import os
from pathlib import Path
from typing import Any

# MCP SDK imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our tool implementations
from tools.pdf_extractor import pdf_extractor
from tools.llm_analyzer import llm_analyzer


# Initialize MCP server
server = Server(
    name=os.getenv("MCP_SERVER_NAME", "nutrition-paper-analyzer"),
    version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
)


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================
# Each @server.list_tools decorator registers a tool that clients can call
# Each @server.call_tool decorator implements the tool's logic


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Tell clients what tools are available.
    
    This function is called automatically by MCP when a client connects.
    It returns metadata about each tool: name, description, input schema.
    
    Think of it as the "menu" of available functions.
    """
    return [
        Tool(
            name="extract_pdf_text",
            description=(
                "Extract text content from a PDF research paper. "
                "This is the first step in analyzing any paper. "
                "Returns the full text with page markers, page count, and status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the PDF file",
                    },
                },
                "required": ["pdf_path"],
            },
        ),
        Tool(
            name="analyze_paper_metadata",
            description=(
                "Extract bibliographic metadata from a research paper using GPT-4o. "
                "Returns: authors, publication year, journal, DOI, country of publication, "
                "title, and paper type. Requires paper text as input."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_text": {
                        "type": "string",
                        "description": "Full text of the paper (from extract_pdf_text)",
                    },
                },
                "required": ["paper_text"],
            },
        ),
        Tool(
            name="analyze_paper_methodology",
            description=(
                "Extract methodology information from a research paper using GPT-4o. "
                "Returns: study sample size, duration, inclusion criteria, "
                "country of population, objective, conclusion, and methodology summary. "
                "Requires paper text as input."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_text": {
                        "type": "string",
                        "description": "Full text of the paper (from extract_pdf_text)",
                    },
                },
                "required": ["paper_text"],
            },
        ),
        Tool(
            name="analyze_full_paper",
            description=(
                "Extract both metadata and methodology in a single operation. "
                "This is more efficient than calling the two separate tools. "
                "Returns complete paper analysis with all fields. "
                "Requires paper text as input."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_text": {
                        "type": "string",
                        "description": "Full text of the paper (from extract_pdf_text)",
                    },
                },
                "required": ["paper_text"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Execute a tool when called by a client.
    
    This function is called automatically by MCP when a client invokes a tool.
    It routes the call to the appropriate tool implementation.
    
    Args:
        name: The tool name (e.g., "extract_pdf_text")
        arguments: Dictionary of arguments passed by the client
        
    Returns:
        List of TextContent objects containing the result
    """
    
    import json
    
    # Route to appropriate tool handler
    if name == "extract_pdf_text":
        # Extract arguments
        pdf_path = arguments.get("pdf_path")
        
        if not pdf_path:
            return [
                TextContent(
                    type="text",
                    text="Error: pdf_path is required",
                )
            ]
        
        # Call our PDF extractor
        result = pdf_extractor.extract_text(pdf_path)
        
        # Format result as JSON string
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]
    
    elif name == "analyze_paper_metadata":
        # Extract arguments
        paper_text = arguments.get("paper_text")
        
        if not paper_text:
            return [
                TextContent(
                    type="text",
                    text="Error: paper_text is required",
                )
            ]
        
        # Call LLM analyzer for metadata
        result = llm_analyzer.analyze_metadata(paper_text)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]
    
    elif name == "analyze_paper_methodology":
        # Extract arguments
        paper_text = arguments.get("paper_text")
        
        if not paper_text:
            return [
                TextContent(
                    type="text",
                    text="Error: paper_text is required",
                )
            ]
        
        # Call LLM analyzer for methodology
        result = llm_analyzer.analyze_methodology(paper_text)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]
    
    elif name == "analyze_full_paper":
        # Extract arguments
        paper_text = arguments.get("paper_text")
        
        if not paper_text:
            return [
                TextContent(
                    type="text",
                    text="Error: paper_text is required",
                )
            ]
        
        # Call LLM analyzer for full analysis
        result = llm_analyzer.analyze_full_paper(paper_text)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )
        ]
    
    else:
        # Unknown tool
        return [
            TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'",
            )
        ]


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

async def main():
    """
    Start the MCP server.
    
    This uses stdio (standard input/output) as the transport mechanism.
    The server listens on stdin for JSON-RPC requests and responds on stdout.
    
    Why stdio?
    - Simple: no need for network ports, HTTP, etc.
    - Secure: client and server run as parent/child processes
    - Standard: works across platforms
    """
    print("Starting Nutrition Paper Analyzer MCP Server...", flush=True)
    print(f"Server: {server.name} v{server.version}", flush=True)
    print("Listening for MCP client connections...\n", flush=True)
    
    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


# Run the server when this script is executed
if __name__ == "__main__":
    # Use asyncio to run the async main function
    asyncio.run(main())
