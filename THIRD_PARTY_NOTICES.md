# Dependencies and attribution

- `vendor/price-pilot`: Price Pilot 0.3.0, upstream https://github.com/wby1121/price-pilot, commit 08fa9193b7e0e30125e48f85a3b369580177c265. Distributed under its original MIT license in `vendor/price-pilot/LICENSE`; original source and author notices are retained.
- `tools/shopping-browser/package-lock.json`: records the exact npm dependency graph. `@playwright/mcp` 0.0.84 and `@modelcontextprotocol/sdk` 1.32.2 are direct dependencies. Their code and installed dependency license files are obtained during `npm ci`; `node_modules` is not included in this source bundle.
- Python dependencies and their applicable licenses are obtained during installation from the requirements declared by the vendored project.

No additional license for the repository's other content is granted by this notice.

Distribution change: removed the redundant Hatch wheel force-include table from the vendored pyproject.toml. The entire price_pilot package already includes its skill directory; recent Hatch versions reject the duplicate archive entries. No Python source was changed.
