# Campaign review decision

Record a human review decision explicitly:

```bash
genforge-marketing radar campaign-review-decision --campaign campaigns/bookmark-launch --reviewer "Reviewer Name" --decision approved --notes "Approved for production"
```

Supported decisions: `approved`, `changes_requested`, `rejected`. Approval is blocked until the quality gate reports the campaign ready for human review. Decisions and UTC timestamps are written to the campaign manifest. Approval only authorizes production workflow; it does not publish content.
