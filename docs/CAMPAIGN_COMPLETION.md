# Campaign completion audit

Run the completion audit programmatically with `campaign_completion_report(campaign_path)`. It is read-only and does not mark a campaign complete. It checks explicit human approval, final campaign status, published/metrics/learning stages, production task completion and asset approval.

Campaign completion is intentionally strict: unresolved items remain visible. Publishing automation remains disabled.
