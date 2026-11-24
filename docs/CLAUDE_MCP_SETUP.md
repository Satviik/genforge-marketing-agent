# Claude MCP setup (local stdio)

The GenForge Marketing MCP server exposes the on-demand planning engine to Claude.
Run it on the same computer/account where Claude Code or Claude Desktop runs.
The first implementation is local-only and does not publish to Instagram.

## 1. Install

Use Python 3.12 or newer. From a terminal in the repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

The install includes the official Python MCP SDK. The server command is
`genforge-marketing-mcp`.

## 2. Create the business profile

Create `genforge-business.json` in the repository root, or place it in `data/profiles/`.
Start with this shape and replace the examples with confirmed GenForge facts:

```json
{
  "business_name": "GenForge",
  "website": "https://genforge.co.in",
  "instagram_handle": "@genforge.lab",
  "business_summary": "Custom 3D printed products and made-to-order designs.",
  "target_audiences": ["people looking for personalised gifts", "3D printing enthusiasts"],
  "brand_voice": ["creative", "helpful", "maker-focused"],
  "content_goals": ["awareness", "inquiries", "sales"],
  "primary_cta": "DM GenForge for a custom order",
  "products": [
    {
      "name": "Replace with a real product",
      "description": "Add only confirmed product details.",
      "category": "3D printed product",
      "differentiators": [],
      "available": true
    }
  ],
  "facts_to_avoid_claiming": []
}
```

Do not leave sample products in the profile. Prices, stock, materials, dimensions,
lead times and product capabilities must be entered only after verification.

## 3. Configure Claude Code

Add an MCP server entry to the user's Claude Code MCP configuration. Replace
the repository path with the absolute path on the team member's computer:

```json
{
  "mcpServers": {
    "genforge-marketing": {
      "command": "C:\\ABSOLUTE\\PATH\\TO\\genforge-marketing-agent\\.venv\\Scripts\\genforge-marketing-mcp.exe",
      "args": [],
      "cwd": "C:\\ABSOLUTE\\PATH\\TO\\genforge-marketing-agent"
    }
  }
}
```

Alternatively, if the environment's PATH resolves the command, use
`genforge-marketing-mcp` as the command. Restart Claude Code after saving.

## 4. Available Claude tools

- `get_marketing_capabilities`: returns tool scope and safety boundaries.
- `load_business_profile`: validates and displays the local business profile.
- `generate_monthly_content_plan`: generates a draft for a requested month.
- `export_content_plan_workbook`: writes an Excel file with exactly `Posts`
  and `Reels` sheets under `data/plans/`.

Planning is on demand. Ask Claude for a specific month and provide the verified
festival/occasion research when available. The occasion JSON has this shape:

```json
{
  "year": 2026,
  "month": 12,
  "market": "India",
  "occasions": [
    {
      "name": "Example occasion",
      "date": "2026-12-25",
      "market": "India",
      "confidence": "suggested",
      "campaign_notes": "Possible seasonal creative angle"
    }
  ]
}
```

A `verified` occasion must include `source_name` or `source_url`. The example
above is illustrative, not a researched recommendation. Dates outside the
requested month or occasions for a different market are rejected.

## Safety and current limitations

- This MCP server creates drafts and workbooks only. It has no Instagram
  publishing tool and cannot mark content approved.
- Do not connect Make.com publishing until the server-side approval workflow
  is implemented and tested.
- The server reads profile JSON supplied to a tool call and writes exports only
  inside the configured data directory's `plans` folder.
- Keep credentials out of the profile JSON and repository. No paid AI provider
  is required for this planning path.
- The current occasion integration validates supplied research; it does not
  automatically research festival dates yet.
