# Google MCP server samples for Python

These samples show how to use the official
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) to call
[Google remote MCP servers](https://docs.cloud.google.com/mcp/overview). Each
sample runs one MCP operation and shows what's specific to Google MCP servers:

-   **Authentication:** an OAuth 2.0 access token from
    [Application Default Credentials (ADC)](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
    and the `x-goog-user-project` quota project header, attached to the SDK's
    HTTP client in [`mcp_auth.py`](mcp_auth.py).
-   **Endpoints:** the Google MCP server URL, passed in as `server_url`, for
    example `https://cloudquotas.googleapis.com/mcp`.
-   **Error handling:** transport, authentication, and protocol errors raise
    `MCPError`, while a tool that fails returns `is_error=True`.

The samples use the SDK's automatic protocol version negotiation, so they work
with servers that support MCP version `2026-07-28` and with earlier servers.

## Samples

| Operation | Sample | Region tag |
| --- | --- | --- |
| `tools/list` | [`list_tools.py`](list_tools.py) | `mcp_tools_list` |
| `tools/call` | [`call_tool.py`](call_tool.py) | `mcp_tools_call` |
| `prompts/list` | [`list_prompts.py`](list_prompts.py) | `mcp_prompts_list` |
| `prompts/get` | [`get_prompt.py`](get_prompt.py) | `mcp_prompts_get` |
| `resources/list` | [`list_resources.py`](list_resources.py) | `mcp_resources_list` |
| `resources/read` | [`read_resource.py`](read_resource.py) | `mcp_resources_read` |
| `resources/templates/list` | [`list_resource_templates.py`](list_resource_templates.py) | `mcp_resource_templates_list` |
| Shared ADC authentication helper | [`mcp_auth.py`](mcp_auth.py) | `mcp_client_auth` |

## Before you begin

1.  Install Python 3.10 or later and the
    [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install).
1.  Set up ADC:

    ```sh
    gcloud auth application-default login
    ```

1.  In your Google Cloud project, [enable the product API](https://docs.cloud.google.com/mcp/enable-disable-mcp-servers)
    for the MCP server that you want to use.
1.  Make sure you have the MCP Tool User (`roles/mcp.toolUser`) role and the
    product roles that the tool, prompt, or resource requires.
1.  Install the dependencies:

    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Run the samples

Replace `PROJECT_ID` with your Google Cloud project ID.

```sh
# List and call tools on the Cloud Quotas MCP server.
python list_tools.py https://cloudquotas.googleapis.com/mcp PROJECT_ID
python call_tool.py https://cloudquotas.googleapis.com/mcp PROJECT_ID list_quota_infos \
    --arguments '{"parent": "projects/PROJECT_ID/locations/global/services/compute.googleapis.com"}'

# List and read resources on the Gemini Cloud Assist MCP server.
python list_resources.py https://geminicloudassist.googleapis.com/mcp PROJECT_ID
python list_resource_templates.py https://geminicloudassist.googleapis.com/mcp PROJECT_ID
python read_resource.py https://geminicloudassist.googleapis.com/mcp PROJECT_ID ui://geminicloudassist/canvas.html

# List and get prompts on the Cloud Run MCP server.
python list_prompts.py https://run.googleapis.com/mcp PROJECT_ID
python get_prompt.py https://run.googleapis.com/mcp PROJECT_ID deploy \
    --arguments '{"project": "PROJECT_ID", "region": "us-central1"}'
```

> **Note:** The Cloud Run `deploy` prompt returns instructions for a model to
> deploy a Cloud Run service by using the `deploy_service_from_file_contents`
> tool. `get_prompt.py` only prints the prompt messages and doesn't run any
> tools. If you pass the messages to an agent that can call tools, the agent
> can create a Cloud Run service in your project.

## Test the samples

The tests call live Google MCP servers with ADC and only read data. The test
project needs the Cloud Quotas, Gemini Cloud Assist, and Cloud Run APIs and MCP servers
enabled, and the test identity needs read access to them.

```sh
pip install -r requirements.txt -r requirements-test.txt
export GOOGLE_CLOUD_PROJECT=PROJECT_ID
pytest samples_test.py
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). Changes to these samples need an
approval from a code owner in [`.github/CODEOWNERS`](../../.github/CODEOWNERS).
