# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Calls a tool on a Google MCP server (tools/call)."""

import argparse
import json

# [START mcp_tools_call]
from typing import Any

import anyio
from mcp import Client, MCPError
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, TextContent

from mcp_auth import create_authorized_http_client


async def call_tool(
    server_url: str,
    project_id: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> CallToolResult:
    """Calls a tool on a Google MCP server.

    Args:
        server_url: The MCP server endpoint, for example
            "https://cloudquotas.googleapis.com/mcp".
        project_id: The Google Cloud project to use for quota and billing.
        tool_name: The tool to call, for example "list_quota_infos".
        arguments: The tool's input arguments, as defined by its input_schema.

    Returns:
        The tool's result.
    """
    async with create_authorized_http_client(project_id) as http_client:
        transport = streamable_http_client(server_url, http_client=http_client)
        # The client negotiates the MCP protocol version with the server.
        async with Client(transport) as client:
            try:
                result = await client.call_tool(tool_name, arguments)
            except MCPError as e:
                # Transport, authentication, and protocol errors raise MCPError.
                print(f"tools/call failed with error {e.code}: {e}")
                raise

    # A tool that fails returns is_error=True instead of raising an exception.
    if result.is_error:
        print(f"The {tool_name} tool returned an error:")

    # Unstructured content, such as text, for the model.
    for block in result.content:
        if isinstance(block, TextContent):
            print(block.text)

    # Structured content that matches the tool's output_schema, if any.
    if result.structured_content is not None:
        print(result.structured_content)

    return result


# [END mcp_tools_call]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server_url", help="The MCP server endpoint URL.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    parser.add_argument("tool_name", help="The name of the tool to call.")
    parser.add_argument(
        "--arguments",
        default="{}",
        help='The tool arguments as a JSON object, for example \'{"parent": "..."}\'.',
    )
    args = parser.parse_args()
    anyio.run(
        call_tool,
        args.server_url,
        args.project_id,
        args.tool_name,
        json.loads(args.arguments),
    )
