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

"""Gets a prompt from a Google MCP server (prompts/get).

This sample only prints the prompt messages that the server returns. It
doesn't send them to a model, so it doesn't run any tools that the prompt
mentions.
"""

import argparse
import json

# [START mcp_prompts_get]
import anyio
from mcp import Client, MCPError
from mcp.client.streamable_http import streamable_http_client
from mcp.types import GetPromptResult, TextContent

from mcp_auth import create_authorized_http_client


async def get_prompt(
    server_url: str,
    project_id: str,
    prompt_name: str,
    arguments: dict[str, str],
) -> GetPromptResult:
    """Gets a rendered prompt from a Google MCP server.

    Args:
        server_url: The MCP server endpoint, for example
            "https://run.googleapis.com/mcp".
        project_id: The Google Cloud project to use for quota and billing.
        prompt_name: The prompt to get, for example "deploy".
        arguments: The prompt arguments. Prompt argument values are always
            strings.

    Returns:
        The prompt description and messages.
    """
    async with create_authorized_http_client(project_id) as http_client:
        transport = streamable_http_client(server_url, http_client=http_client)
        # The client negotiates the MCP protocol version with the server.
        async with Client(transport) as client:
            try:
                result = await client.get_prompt(prompt_name, arguments)
            except MCPError as e:
                print(f"prompts/get failed with error {e.code}: {e}")
                raise

    if result.description:
        print(result.description)

    # The rendered messages that an MCP client application passes to a model.
    for message in result.messages:
        if isinstance(message.content, TextContent):
            print(f"{message.role}: {message.content.text}")

    return result


# [END mcp_prompts_get]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server_url", help="The MCP server endpoint URL.")
    parser.add_argument("project_id", help="Your Google Cloud project ID.")
    parser.add_argument("prompt_name", help="The name of the prompt to get.")
    parser.add_argument(
        "--arguments",
        default="{}",
        help='The prompt arguments as a JSON object of strings, for example \'{"region": "us-central1"}\'.',
    )
    args = parser.parse_args()
    anyio.run(
        get_prompt,
        args.server_url,
        args.project_id,
        args.prompt_name,
        json.loads(args.arguments),
    )
