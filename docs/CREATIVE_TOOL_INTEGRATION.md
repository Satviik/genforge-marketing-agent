# Creative-tool integration

## Current milestone: provider boundary only

The marketing agent now has provider-neutral contracts for image and video generation. A provider can be connected later without changing planning, content drafting, or approval models. The default provider is disabled and raises a clear error; it never returns placeholder files or pretends generation succeeded.

## Product-accuracy rules

- Supply genuine GenForge product photographs as reference images whenever a generated composition depicts a real product.
- Preserve reference geometry. Do not let a generative model redesign, add, remove, or distort product parts.
- Generate backgrounds, lighting, scene styling, and composition around the reference product where the selected provider supports reference-image conditioning.
- Keep typography and logos out of generated pixels; add approved copy and brand marks in a deterministic post-production step.
- Keep source image paths, provider name, prompt, warnings, and output path/URL in the generated-asset record.
- Generated assets are drafts. They do not enter the publishing queue or publish automatically.

## Provider selection still required

No image/video provider has been selected or connected. The adapter contract intentionally does not assume a particular MCP server, API, subscription, or local model. Before implementing a concrete adapter, evaluate candidate tools for:
1. reference-image / image-to-image support and fidelity controls;
2. vertical video generation, duration, and image-to-video support;
3. output format, resolution, watermark, and commercial-use terms;
4. API/MCP availability, authentication, rate limits, and cost;
5. ability to return a stable downloadable asset and generation metadata.

The next implementation step is to evaluate the actual MCP tools available to the GenForge workflow, select a provider, then add a real adapter and mocked contract tests. Instagram screening CLI integration remains deferred until all marketing components are complete.
