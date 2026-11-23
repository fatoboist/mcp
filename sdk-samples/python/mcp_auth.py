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

"""Shared authentication helper for the Google MCP server SDK samples."""

# [START mcp_client_auth]
import google.auth
from google.auth.transport.requests import Request
import httpx2

CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


def create_authorized_http_client(project_id: str) -> httpx2.AsyncClient:
    """Creates an HTTP client that authenticates to Google MCP servers.

    The client uses Application Default Credentials (ADC). Set up ADC with
    `gcloud auth application-default login` or by attaching a service account.

    Args:
        project_id: The Google Cloud project to use for quota and billing.

    Returns:
        An httpx2.AsyncClient to pass to the MCP Streamable HTTP transport.
    """
    credentials, _ = google.auth.default(scopes=[CLOUD_PLATFORM_SCOPE])
    credentials.refresh(Request())

    # Google MCP servers require an OAuth 2.0 access token and a quota project.
    # The MCP SDK sends these headers with every request.
    return httpx2.AsyncClient(
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "x-goog-user-project": project_id,
        },
        timeout=httpx2.Timeout(30.0, read=300.0),
    )


# [END mcp_client_auth]
