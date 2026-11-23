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

"""Tests the samples against live Google MCP servers.

The tests use Application Default Credentials and the project in the
GOOGLE_CLOUD_PROJECT environment variable. They only read data: the prompts
test checks the messages that prompts/get returns and never sends them to a
model or calls a tool.
"""

import os

import pytest

from call_tool import call_tool
from get_prompt import get_prompt
from list_prompts import list_prompts
from list_resource_templates import list_resource_templates
from list_resources import list_resources
from list_tools import list_tools
from read_resource import read_resource

pytestmark = pytest.mark.anyio

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
REGION = "us-central1"

# Tools: Cloud Quotas. The list_quota_infos tool is read-only.
CLOUD_QUOTAS_MCP_URL = "https://cloudquotas.googleapis.com/mcp"
TOOL_NAME = "list_quota_infos"

# Resources: Gemini Cloud Assist. The canvas resource is an MCP App UI
# resource.
GEMINI_CLOUD_ASSIST_MCP_URL = "https://geminicloudassist.googleapis.com/mcp"
RESOURCE_URI = "ui://geminicloudassist/canvas.html"

# Prompts: Cloud Run. The deploy prompt suggests a tool that deploys a
# service, but prompts/get only returns a templated message.
CLOUD_RUN_MCP_URL = "https://run.googleapis.com/mcp"
PROMPT_NAME = "deploy"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_list_tools(capsys: pytest.CaptureFixture[str]) -> None:
    tools = await list_tools(CLOUD_QUOTAS_MCP_URL, PROJECT_ID)

    assert TOOL_NAME in [tool.name for tool in tools]
    assert TOOL_NAME in capsys.readouterr().out


async def test_call_tool() -> None:
    result = await call_tool(
        CLOUD_QUOTAS_MCP_URL,
        PROJECT_ID,
        TOOL_NAME,
        {"parent": f"projects/{PROJECT_ID}/locations/global/services/compute.googleapis.com"},
    )

    assert not result.is_error
    assert result.content or result.structured_content is not None


async def test_list_prompts() -> None:
    prompts = await list_prompts(CLOUD_RUN_MCP_URL, PROJECT_ID)

    assert PROMPT_NAME in [prompt.name for prompt in prompts]


async def test_get_prompt(capsys: pytest.CaptureFixture[str]) -> None:
    result = await get_prompt(
        CLOUD_RUN_MCP_URL,
        PROJECT_ID,
        PROMPT_NAME,
        {"project": PROJECT_ID, "region": REGION},
    )

    # An empty response means the server didn't render the prompt.
    assert result.messages
    assert result.messages[0].role == "user"
    expected_text = (
        "Use the deploy_service_from_file_contents tool to deploy the current "
        f"folder in project {PROJECT_ID} in region {REGION}"
    )
    assert expected_text in result.messages[0].content.text
    assert expected_text in capsys.readouterr().out


async def test_list_resources() -> None:
    resources = await list_resources(GEMINI_CLOUD_ASSIST_MCP_URL, PROJECT_ID)

    assert RESOURCE_URI in [resource.uri for resource in resources]


async def test_list_resource_templates() -> None:
    # The server doesn't provide templates, so only check the call succeeds.
    templates = await list_resource_templates(GEMINI_CLOUD_ASSIST_MCP_URL, PROJECT_ID)

    assert isinstance(templates, list)


async def test_read_resource() -> None:
    result = await read_resource(GEMINI_CLOUD_ASSIST_MCP_URL, PROJECT_ID, RESOURCE_URI)

    assert result.contents
    contents = result.contents[0]
    assert contents.uri == RESOURCE_URI
    assert contents.mime_type == "text/html;profile=mcp-app"
    assert contents.text
