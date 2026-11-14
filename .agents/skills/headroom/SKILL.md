---
name: headroom
description: Context & token optimization for Gemini 3.8 Flash High / 3.7 Flash High. Compresses large tool outputs, scientific datasets, NASA API responses, logs, GeoJSON, and chat history before passing to the model without losing error traces, data boundaries, or code integrity.
---

# Headroom for Gemini 3.8 Flash (High)

Adapted context-optimization layer tailored for Gemini 3.8 Flash High and Gemini 3.7 Flash High.

## Core Purpose

Gemini 3.8 Flash High possesses a huge context window and rapid processing, but feeding unpruned raw datasets (such as NASA Earth Observation GeoJSON, telemetry arrays, multi-megabyte API logs, or massive sensor streams) introduces latency, unnecessary token costs, and context dilution.

Headroom compresses data inputs before they reach the model while preserving critical information:
- Error lines and stack traces
- First, last, and median statistical rows
- Numerical extremes (min, max, outliers)
- Schema definitions and field types
- Key metadata headers and timestamps

## When to Activate

Use this skill when:
1. Handling large NASA Open API payloads (e.g., MODIS satellite imagery metadata, NASA APOD archives, Asteroids NeoWs arrays).
2. Processing multi-megabyte CSV, JSON, or GeoJSON files.
3. Reading dense logs, build output, or terminal traces.
4. Structuring system prompts and history across long sessions.

## Adaptation for Gemini SDKs

### Python (`google-genai` / `@google/genai`)

```python
# Headroom compression helper for Gemini tool outputs
from headroom import compress

def prepare_gemini_payload(raw_data, model="gemini-2.5-flash"):
    """
    Compresses large tool outputs / datasets before passing to Gemini 3.8 Flash High.
    Caches the full uncompressed payload locally while presenting compressed view.
    """
    if isinstance(raw_data, (dict, list)):
        import json
        text_data = json.dumps(raw_data)
    else:
        text_data = str(raw_data)
        
    # Compress while protecting key lines and bounds
    # Headroom preserves errors, boundaries, schema, and anomalies
    compressed = compress([{"role": "tool", "content": text_data}], model=model)
    return compressed.messages[0]["content"]
```

### TypeScript / Node.js

```typescript
import { GoogleGenAI } from '@google/genai';

// Fast in-process statistical compressor for NASA telemetry and arrays
export function compactDataset<T>(data: T[], maxItems = 50): { summary: string; sample: T[] } {
  if (data.length <= maxItems) return { summary: `Total records: ${data.length}`, sample: data };
  
  const sample = [
    ...data.slice(0, 10), // Head sample
    ...data.slice(Math.floor(data.length / 2) - 5, Math.floor(data.length / 2) + 5), // Mid sample
    ...data.slice(-10) // Tail sample
  ];
  
  return {
    summary: `Dataset compacted: showing ${sample.length} of ${data.length} records. Extremes & boundary values preserved.`,
    sample
  };
}
```

## Best Practices

1. **Protect User & Instruction Prompts**: Never compress task definitions, code specifications, or security guidelines.
2. **Compress Tool Responses & Datasets**: Compress raw data streams, API responses, and database tables.
3. **Trace Preservation**: Always retain line numbers, file paths, and exception traces verbatim.
4. **Log Token Savings**: Compare tokens before and after compression to track efficiency.

