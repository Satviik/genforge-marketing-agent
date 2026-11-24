# Original Creative Generator

Generate an original Reel brief from product facts and optional creative-breakdown evidence.

This initial implementation is deterministic and local. It does not call a model or paid API. It produces a structured draft containing concept options, hook options, scene timing, visual/voiceover guidance, editing direction, caption, CTA options, and adaptation notes. It borrows broad structural mechanics only—not the reference's wording, footage, product, or distinctive visuals.

## CLI

```bash
genforge-marketing radar generate-creative --product "Custom bookmark" --description "Personalized 3D printed bookmark" --objective inquiries --audience "book lovers and gift buyers" --duration 20 --breakdown output/creative-breakdown.json --output output/original-reel-brief.json
```

Omit `--breakdown` to generate without reference study. Review all draft claims and production notes before use.
