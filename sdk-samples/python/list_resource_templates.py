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

"""Lists the resource templates on a Google MCP server (resources/templates/list)."""

import argparse

# [START mcp_resource_templates_list]
import anyio
from mcp import Client, MCPError
from mcp.client.streamable_http import streamable_http_client
from mcp.types import ResourceTemplate

from mcp_auth import create_authorized_http_client


async def list_resource_templates(
    server_url: str, project_id: str
) -> list[ResourceTemplate]:
    """Lists all resource templates on a Google MCP server.

    Args:
        server_url: The MCP server endpoint, for example
            "https://geminicloudassist.googleapis.com/mcp".
        project_id: The Google Cloud project to use for quota and billing.

    Returns:
        The resource templates that the server provides. A server that
        doesn't provide any templates returns an empty list.
    """
    templates: list[ResourceTemplate] = []
    async with create_authorized_http_client(project_id) as http_client:
        transport = streamable_http_client(server_url, http_client=http_client)
        # The client negotiates the MCP protocol version with the server.
        async with Client(transport) as client:
            try:
                # Follow next_cursor until the server returns every page.
                cursor = None
                while True:
                    result = await client.list_resource_templates(cursor=cursor)
                    templates.extend(result.resource_templates)
                    cursor = result.next_cursor
                    if not cursor:
                        break
            except MCPError as e:
                print(f"resources/templates/list failed with error {e.code}: {e}")
                raise

    for template in templates:
        print(f"{template.uri_template} ({template.mime_type}): {template.name}")
    return templates


# [END mcp_resource_templates_list]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server_url", help="The MCP server endpoint URL.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    args = parser.parse_args()
    anyio.run(list_resource_templates, args.server_url, args.project_id)
