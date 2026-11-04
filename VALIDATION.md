# Validation record — v0.1.0

Package prepared on 2026-11-04 for Windows. Checks were performed in an isolated staging directory with Node.js 24.17.0, Python 3.12.14 and PowerShell 7.

Passed:

- Both distributed skills pass skill-creator `quick_validate.py` with UTF-8 enabled.
- All six JavaScript modules pass `node --check`; packaged Python source parses successfully.
- The PowerShell installer parses and successfully installs npm dependencies and a local Price Pilot virtual environment into the staging bundle.
- Skills install into a separate validation home. Repeating installation preserves both previous skills in timestamped backups, and installed entry points match the package hashes.
- Price Pilot 0.3.0 installs from the vendored source with its skill resource included. The redundant Hatch wheel force-include setting was removed in this distribution to prevent duplicate archive entries; Python source is unchanged.
- Five isolated workflow tests pass: SKU/quantity/currency/condition separation; verified landed-price handling; invalid evidence rejection; search-only evidence remains unverified; and real Price Pilot normalization of a price below ten.
- Relative references in the two skills and YAML metadata parse successfully. Tracked files were checked for personal installation paths, credential patterns and excluded runtime artifacts.

The complete MCP/browser protocol test was intentionally not run against shared services. No live marketplace login, coupon collection, actual discount application, cart mutation or Pinduoduo favorite mutation was performed for this packaging task. Those outcomes require current platform evidence and are not established by the synthetic workflow tests.

The ZIP is generated from the committed source tree. `PACKAGE_MANIFEST.json` lists SHA-256 values for source files other than the manifest itself; a sibling `.sha256` file records the ZIP checksum.
