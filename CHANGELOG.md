# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog.

## [Unreleased]

## [2026-04-03]

### Added
- Introduced a formal changelog workflow to record every update in GitHub.
- Added a pull request template checklist to require update notes before merge.

### Changed
- Improved loading overlay flow: avoid initial map flash, support "ready then click to enter", and keep status transitions clearer.
- Refined settlement analysis interaction so comparison behavior is aligned with existing compare-mode logic and chart area usage.

### Fixed
- Fixed multiple Chinese text display issues in loader/status copy.
- Fixed inconsistencies around loading-ready state where spinner/progress could continue after core resources were ready.

---

## How to use this file

For each update:
1. Add new items under `## [Unreleased]` while developing.
2. Before release/merge, move those items to a date section like `## [YYYY-MM-DD]`.
3. Keep entries short and user-facing: what changed, why it matters.

