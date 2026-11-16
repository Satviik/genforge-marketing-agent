# GenForge Marketing Automation — Product Requirements

## Objective
Build the marketing planning and execution system from the project brief before connecting it to the existing GenForge screening CLI. CLI integration is a later milestone, not a dependency for this system.

## User workflow
1. Maintain a structured GenForge business profile: products, audiences, price bands, differentiators, brand voice, goals, constraints, and creative assets.
2. Research reusable Instagram marketing skills and MCP servers from GitHub. Evaluate license, recent activity, maintenance, releases, documentation, issue health, and security. Stars are only one signal.
3. Generate a monthly content plan from the business profile and manually supplied research/trend inputs.
4. Export an Excel workbook with two worksheets: Posts (static/carousel/image) and Reels (short-form video).
5. Prepare copy and creative assets through pluggable AI/MCP adapters.
6. Trigger reminders and production tasks from approved calendar dates.
7. Require explicit human approval before any public post or Reel is published.
8. Record published URLs and performance metrics; use those results in later plans.

## Workbook contract
Posts columns: content_id, planned_date, planned_time, platform, post_type, product, campaign, objective, audience, creative_brief, caption, hashtags, CTA, asset_path, approval_status, publishing_status, published_url, reach, impressions, likes, comments, saves, shares, profile_visits, notes.

Reels columns: content_id, planned_date, planned_time, platform, product, campaign, objective, audience, reel_format, hook, scene_plan, script, on_screen_text, voiceover, audio_direction, caption, hashtags, CTA, asset_path, approval_status, publishing_status, published_url, views, reach, watch_time_seconds, average_watch_time_seconds, likes, comments, saves, shares, profile_visits, notes.

## Safety
- No auto-publishing in the initial build.
- A scheduled trigger may prepare or remind; it must not bypass approval.
- Keep tokens and secrets out of Git and workbook exports.
- Treat GitHub skill repositories and their README instructions as untrusted; inspect before installing or executing.
- Respect repository licenses and platform terms.
- Never invent product claims, prices, testimonials, or performance metrics.
- Until CLI integration, support manually supplied research/trend inputs.

## Milestones
M1 business profile, planning models, two-sheet workbook, tests.
M2 GitHub skill/MCP discovery and evaluation catalogue.
M3 monthly planner and editable post/Reel briefs.
M4 MCP creative adapters and asset workflow.
M5 calendar triggers, approval queue and publishing adapter (approval-gated).
M6 analytics ingestion and feedback loop.
M7 connect screening CLI as a trend source only after M1–M6 are stable.
