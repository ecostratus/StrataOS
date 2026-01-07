# API Endpoints Documentation

## Overview

This document lists all API endpoints and service URLs used by the personal operating system.

## Job Discovery APIs

### LinkedIn Jobs API
- **Base URL**: `https://api.linkedin.com/v2/`
- **Authentication**: OAuth 2.0
- **Docs**: https://docs.microsoft.com/en-us/linkedin/
- **Rate Limits**: Varies by API tier
- **Required Scopes**: `r_basicprofile`, `r_jobs`

**Endpoints**:
- Search Jobs: `GET /jobs?keywords={keywords}&location={location}`
- Get Job Details: `GET /jobs/{jobId}`

### Indeed Publisher API
- **Base URL**: `https://api.indeed.com/ads/apisearch`
- **Authentication**: API key (publisher key)
- **Docs**: https://opensource.indeedeng.io/api-documentation/
- **Rate Limits**: Throttling based on account
- **Format**: XML or JSON

**Parameters**:
- `publisher`: Your publisher key
- `q`: Search query
- `l`: Location
- `format`: `json` or `xml`
- `limit`: Results per page (max 25)

**Example**:
```
https://api.indeed.com/ads/apisearch?publisher={KEY}&q=software+engineer&l=san+francisco&format=json&limit=25
```

### GitHub Jobs API (Deprecated)
- **Status**: Deprecated as of May 2021
- **Alternative**: Use job board APIs or scraping

## AI Services

### OpenAI API
- **Base URL**: `https://api.openai.com/v1/`
- **Authentication**: Bearer token (API key)
- **Docs**: https://platform.openai.com/docs/api-reference
- **Rate Limits**: Varies by account tier

**Endpoints**:
- Chat Completions: `POST /chat/completions`
- Completions: `POST /completions`
- Models: `GET /models`

**Example Request**:
```json
POST /v1/chat/completions
{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "Your prompt"}],
  "temperature": 0.7
}
```

### Azure OpenAI Service
- **Base URL**: `https://{resource-name}.openai.azure.com/`
- **Authentication**: API key
- **Docs**: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Rate Limits**: Configurable per deployment

**Endpoints**:
- Chat Completions: `POST /openai/deployments/{deployment-id}/chat/completions?api-version=2023-05-15`

## Microsoft 365 APIs

### Microsoft Graph API
- **Base URL**: `https://graph.microsoft.com/v1.0/`
- **Authentication**: OAuth 2.0 (Azure AD)
- **Docs**: https://docs.microsoft.com/en-us/graph/
- **Rate Limits**: Service-specific throttling

**Endpoints**:
- Excel Workbooks: `GET /me/drive/items/{item-id}/workbook`
- Update Range: `PATCH /me/drive/items/{item-id}/workbook/worksheets/{sheet}/range(address='{range}')`
- Teams Messages: `POST /teams/{team-id}/channels/{channel-id}/messages`

### SharePoint REST API
- **Base URL**: `https://{tenant}.sharepoint.com/_api/`
- **Authentication**: OAuth 2.0 or app-only
- **Docs**: https://docs.microsoft.com/en-us/sharepoint/dev/

**Endpoints**:
- Get File: `GET /web/GetFileByServerRelativeUrl('{path}')/$value`
- Upload File: `POST /web/GetFolderByServerRelativeUrl('{path}')/Files/add(url='{filename}',overwrite=true)`

## Copilot Studio

### Power Automate Flows
- **Trigger URL**: Generated per flow
- **Authentication**: HTTP trigger with key or OAuth
- **Docs**: https://docs.microsoft.com/en-us/power-automate/

**Trigger Endpoint Format**:
```
https://prod-XX.northcentralus.logic.azure.com:443/workflows/{workflow-id}/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig={signature}
```

## Company Research APIs

### Clearbit Enrichment API
- **Base URL**: `https://company.clearbit.com/v2/`
- **Authentication**: Bearer token (API key)
- **Docs**: https://clearbit.com/docs
- **Rate Limits**: Plan-dependent

**Endpoints**:
- Company Lookup: `GET /companies/find?domain={domain}`

### Crunchbase API
- **Base URL**: `https://api.crunchbase.com/v3.1/`
- **Authentication**: API key
- **Docs**: https://data.crunchbase.com/docs
- **Rate Limits**: 200 requests/minute

**Endpoints**:
- Organization: `GET /organizations/{permalink}`
- Search: `GET /organizations?name={name}`

## Email Services

### Gmail SMTP
- **Server**: `smtp.gmail.com`
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: Username/password or OAuth 2.0
- **Docs**: https://support.google.com/mail/answer/7126229

**Configuration**:
```python
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-app-password"
```

### SendGrid API
- **Base URL**: `https://api.sendgrid.com/v3/`
- **Authentication**: Bearer token (API key)
- **Docs**: https://docs.sendgrid.com/api-reference
- **Rate Limits**: Plan-dependent

**Endpoints**:
- Send Email: `POST /mail/send`

## Notification Services

### Microsoft Teams Incoming Webhooks
- **URL**: Generated per channel connector
- **Authentication**: URL contains secret
- **Docs**: https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/

**Example Request**:
```json
POST {webhook-url}
{
  "text": "Notification message",
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "summary": "Summary text"
}
```

### Slack Incoming Webhooks
- **URL**: Generated per workspace
- **Authentication**: URL contains secret
- **Docs**: https://api.slack.com/messaging/webhooks

**Example Request**:
```json
POST {webhook-url}
{
  "text": "Notification message",
  "blocks": [...]
}
```

## Rate Limiting Best Practices

### General Guidelines
1. **Respect rate limits**: Always check API documentation
2. **Implement exponential backoff**: Retry with increasing delays
3. **Cache responses**: Avoid duplicate requests
4. **Batch requests**: Use batch endpoints when available
5. **Monitor usage**: Track API consumption

### Example Implementation
```python
import time
from functools import wraps

def rate_limit(calls_per_minute):
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = (60.0 / calls_per_minute) - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

## Error Handling

### Common HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Service temporarily unavailable

### Retry Strategy
- **Retry on**: 429, 500, 502, 503, 504
- **Don't retry on**: 400, 401, 403, 404
- **Max retries**: 3-5 attempts
- **Backoff**: Exponential (1s, 2s, 4s, 8s, 16s)

## Security Considerations

1. **Never commit API keys**: Use environment variables
2. **Use HTTPS**: Always use secure connections
3. **Rotate keys regularly**: Quarterly or after exposure
4. **Minimum scopes**: Request only necessary permissions
5. **Monitor usage**: Watch for unusual activity
6. **Secure storage**: Use secrets management (Azure Key Vault, etc.)

## Testing Endpoints

### Tools
- **Postman**: GUI for API testing
- **curl**: Command-line HTTP client
- **httpie**: Modern command-line HTTP client
- **Python requests**: Programmatic testing

### Example curl Test
```bash
curl -X GET "https://api.example.com/endpoint" \
  -H "X-Demo-Auth: example-token" \
  -H "Content-Type: application/json"
```

## Support and Resources

- **OpenAI Platform**: https://platform.openai.com/docs
- **Microsoft Graph**: https://developer.microsoft.com/en-us/graph
- **LinkedIn Developers**: https://www.linkedin.com/developers/
- **Indeed Publisher**: https://www.indeed.com/publishers
