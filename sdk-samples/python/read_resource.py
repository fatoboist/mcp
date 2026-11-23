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

"""Reads a resource from a Google MCP server (resources/read)."""

import argparse

# [START mcp_resources_read]
import anyio
from mcp import Client, MCPError
from mcp.client.streamable_http import streamable_http_client
from mcp.types import BlobResourceContents, ReadResourceResult, TextResourceContents

from mcp_auth import create_authorized_http_client


async def read_resource(
    server_url: str, project_id: str, uri: str
) -> ReadResourceResult:
    """Reads a resource by URI from a Google MCP server.

    Args:
        server_url: The MCP server endpoint, for example
            "https://geminicloudassist.googleapis.com/mcp".
        project_id: The Google Cloud project to use for quota and billing.
        uri: The URI of a resource from resources/list, or a URI that matches
            a template from resources/templates/list, for example
            "ui://geminicloudassist/canvas.html".

    Returns:
        The resource contents.
    """
    async with create_authorized_http_client(project_id) as http_client:
        transport = streamable_http_client(server_url, http_client=http_client)
        # The client negotiates the MCP protocol version with the server.
        async with Client(transport) as client:
            try:
                result = await client.read_resource(uri)
            except MCPError as e:
                print(f"resources/read failed with error {e.code}: {e}")
                raise

    for contents in result.contents:
        if isinstance(contents, TextResourceContents):
            # MCP App UI resources use the text/html;profile=mcp-app MIME type.
            print(f"{contents.uri} ({contents.mime_type}): {len(contents.text)} characters")
        elif isinstance(contents, BlobResourceContents):
            # Binary content is base64-encoded.
            print(f"{contents.uri} ({contents.mime_type}): {len(contents.blob)} base64 characters")

    return result


# [END mcp_resources_read]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server_url", help="The MCP server endpoint URL.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    parser.add_argument("uri", help="The URI of the resource to read.")
    args = parser.parse_args()
    anyio.run(read_resource, args.server_url, args.project_id, args.uri)
