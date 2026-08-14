# Scripts

Auto-indexed script repository. Drag scripts into `categories/`, push, and `scripts.json` updates automatically.

## Quick Start

1. **Add scripts:** Drop `.js`, `.ts`, or `.py` files into `categories/{web-tools,utilities,data-processing,automation}/`
2. **Commit & push**
3. **Done** — GitHub Actions auto-indexes them into `scripts.json`

## Metadata Format (Optional)

Add JSDoc to your scripts for better indexing:

```javascript
/**
 * @name URL Query Parser
 * @description Extracts and decodes URL query parameters
 * @tags url, parsing, query-string
 */

function parseQuery(queryString) {
  // ...
}
```

Or just a comment:
```javascript
// URL query parser - extracts query string parameters
```

If you skip comments, auto-generation creates metadata from filename and folder.

## scripts.json

Auto-generated. Contains:
- Script metadata (name, description, tags, category)
- File paths
- Last updated timestamps
- Content hashes (detects changes)
- Stats (total, new, updated)

## Workflow

| Action | Result |
|--------|--------|
| Push new script to `categories/` | Added to `scripts.json` |
| Modify existing script | Entry updated with new hash |
| Delete script | Removed from `scripts.json` |
| No script changes | No unnecessary commits |

## Structure

```
scripts/
├── .github/
│   ├── workflows/
│   │   └── auto-index.yml
│   └── scripts/
│       └── index-scripts.js
├── categories/
│   ├── web-tools/
│   ├── utilities/
│   ├── data-processing/
│   └── automation/
├── scripts.json
└── README.md
```

## Browser Workflow

1. Open repo in GitHub web editor
2. Drag `.js` files into `categories/` folders
3. Commit & push
4. Check "Actions" tab to watch workflow run
5. `scripts.json` updates automatically
