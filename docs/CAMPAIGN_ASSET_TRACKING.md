# Campaign asset management

Assets are stored under `production/assets/` within a campaign. The handoff manifest tracks asset ID, type, status, current file, revision history, and status changes.

States: `draft`, `review`, `approved`, `rejected`.

```bash
genforge-marketing radar campaign-asset-add --campaign campaigns/bookmark-launch --file output/mockup.png --name "Product mockup" --type image
genforge-marketing radar campaign-asset-list --campaign campaigns/bookmark-launch
genforge-marketing radar campaign-asset-revise --campaign campaigns/bookmark-launch --asset-id asset-001 --file output/mockup-v2.png --notes "Corrected details"
genforge-marketing radar campaign-asset-status --campaign campaigns/bookmark-launch --asset-id asset-001 --status approved --notes "Reviewed"
```

Every revision is copied as a new version; earlier versions are preserved. Asset management requires explicit campaign approval and an existing production handoff. Approval here is for the asset, not for campaign publishing.
