# Content Planning Decisions

## Decision: on-demand planning

Monthly content plans are generated only when a team member requests them through Claude/MCP or the CLI. Do not automatically create a new monthly plan on the first day of each month.

## Why

GenForge's marketing calendar is dynamic. Festival dates, seasonal opportunities, product launches, inventory, audience response and emerging trends can change the right content mix from month to month. A fixed recurring generation job would make assumptions that may no longer be relevant.

## Planning inputs

When a plan is requested, the planning workflow should use:

- Requested calendar month and year.
- Current GenForge business profile and product catalogue.
- Brand voice, target audiences, goals and constraints.
- Relevant festivals and seasonal occasions for the target market, with dates and source/evidence where available.
- Current trend research supplied to the system. Until the screening CLI integration milestone, trends may be entered manually or loaded from fixtures.
- Requested or configured posting frequency and preferred posting windows.
- Existing calendar entries and their lifecycle states.

The planner must distinguish verified dates and facts from suggestions or assumptions. It must not invent festival dates, product claims, prices, discounts, inventory or performance metrics.

## Workbook contract

Every generated monthly plan exports an Excel workbook with exactly two planning worksheets:

1. `Posts` — static, image and carousel content.
2. `Reels` — short-form video content.

The workbook remains editable and is accompanied by structured plan data used by the agent and MCP tools.

## Plan revision

A team member may ask Claude to revise an existing plan when a festival, trend, product launch or business priority changes.

Revisions must preserve already published entries and must not silently overwrite approved entries. Draft entries may be regenerated or rescheduled. Approved entries require an explicit change/reapproval workflow before their approved content or schedule is altered. The system should retain revision history so the team can inspect what changed and why.

## Automation boundary

Scheduled triggers may remind the team, prepare due drafts, or notify reviewers based on an existing plan. They must not independently generate a new monthly plan or publish content without the required human approval.

Make.com is the intended scheduling/automation and publishing integration. The MCP server remains the authority for content status and approval checks. A publish request must be rejected unless the content is explicitly approved.

## Acceptance criteria

- A new monthly plan is created only after an explicit request.
- A request can include the target month/year and optional campaign or festival focus.
- Planning considers relevant festivals and seasonal opportunities without treating unverified suggestions as facts.
- The workbook contains exactly the `Posts` and `Reels` worksheets.
- A revision leaves published content unchanged.
- Approved content cannot be silently changed; changes require explicit reapproval.
- Scheduled automation can act on existing approved plans but cannot bypass approval or autonomously publish drafts.
