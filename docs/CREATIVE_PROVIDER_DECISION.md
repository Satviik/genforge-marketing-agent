# Creative provider evaluation and decision

Evaluation date: 2026-11-16

## Decision

Use a two-provider pipeline rather than forcing still-image editing and video generation through one model:

1. **Still images: reference-conditioned image editing.** Shortlist `xieyuanqing/image-mcp` (GPT Image 2 MCP) because it exposes `edit_image`, accepts 1–8 reference images, and supports iterative edit sessions. This matches product-photography compositions where the actual GenForge product must remain the source of truth.
2. **Reels: MiniMax video generation.** Shortlist the official `MiniMax-AI/MiniMax-MCP` server. Its MCP README exposes `generate_video` and `query_video_generation`; its implementation accepts a `first_frame_image` in video generation. The MiniMax video API also documents image-to-video and first/last-frame workflows.

Links:
- https://github.com/xieyuanqing/image-mcp
- https://github.com/MiniMax-AI/MiniMax-MCP
- https://platform.minimax.io/docs/guides/video-generation

## Why not use MiniMax for everything?

The official MiniMax MCP README lists `text_to_image` and `generate_video`, but its published MCP tool table does not make reference-image editing for still-image generation as clear as the dedicated GPT Image MCP's `edit_image` contract. Prefer the tool with an explicit reference-edit interface for product stills. MiniMax can then animate an approved still as the first frame of a Reel.

## Product-accuracy workflow

1. User supplies one or more real photographs of the printed product.
2. Still-image adapter uses those photographs as edit references; ask for a new background, lighting, camera framing, and scene only.
3. Human reviews the still and confirms that shape, dimensions, colours, printed details, and accessories remain faithful.
4. The approved still is passed as the first frame to the video adapter. Prompt only for restrained camera movement or scene motion; do not ask the video model to redesign the product.
5. Human reviews the resulting clip, caption, soundtrack rights, and claims before it can enter the publishing approval queue.

## Trade-offs and constraints

| Candidate | Strength | Limitation / risk | Proposed role |
|---|---|---|---|
| GPT Image 2 MCP | Explicit multi-reference `edit_image` and iterative edit sessions | Requires OpenAI API access; image model may still alter small product details; not a video generator | Product stills and campaign compositions |
| Official MiniMax MCP | Official server, image/video endpoints, asynchronous video task query, first-frame support in implementation | API usage is paid; verify exact MCP parameter exposure and output handling in a local smoke test | Image-to-video Reels |
| Local mcp-imagegen | Local/private image editing with reference images and open-weight backend options | Hardware/model setup and quality vary; video not its focus | Optional later low-cost/local experiment |

## Security and release gates

- Do not install or run third-party MCP servers automatically.
- Do not add API keys to source control or logs.
- Pin reviewed versions/commits and inspect package dependencies before installation.
- Treat generated outputs as unapproved drafts.
- Record provider, model, prompt, input reference paths, output path, warnings, and generation metadata.
- Never auto-publish. Publishing remains blocked until a human explicitly approves the exact asset and caption.

## Next engineering step

Implement the still-image adapter first against a mocked MCP transport, then a separately configured MiniMax video adapter. Verify reference-image paths, file download/persistence, timeouts, async task polling, error handling, and asset provenance. Only then run a paid smoke test with one real GenForge product photograph. No provider has been installed or called yet.
