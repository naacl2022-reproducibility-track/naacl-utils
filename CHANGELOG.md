# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [v0.4.2](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.4.2) - 2022-05-10

### Fixed

- Fixed bug caused when certain bytes in the logs can't be decoded.

## [v0.4.1](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.4.1) - 2022-04-01

### Fixed

- Caught degenerate case where expected output file might be empty or only contain empty lines.

## [v0.4.0](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.4.0) - 2022-03-31

### Changed

- A diff of the actual vs. expected logs is now printed when there's a mismatch with `naacl-utils verify`.
- `naacl-utils verify` now automatically uploads results to Beaker.

## [v0.3.0](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.3.0) - 2022-02-22

### Changed

- `naacl-utils verify` now takes a path for the expected output, instead of a string.

## [v0.2.0](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.2.0) - 2022-01-19

### Added

- Added `naacl-utils verify` command.

## [v0.1.5](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.5) - 2021-12-14

### Added

- Added `--force` flag to `setup` command to redo setup.

### Changed

- Various changes to make the CLI more robust to edge cases.

## [v0.1.4](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.4) - 2021-12-14

### Fixed

- Fixed bug where new version of local image would not be uploaded to Beaker.

## [v0.1.3](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.3) - 2021-12-09

### Added

- Better test coverage, including testing on Windows.
- Warn when a newer version exists.

## [v0.1.2](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.2) - 2021-12-08

### Fixed

- Fixed bug with `create_image()` when workspace doesn't exist yet.

## [v0.1.1](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.1) - 2021-12-08

### Fixed

- Fixed bug with saving Beaker config in `setup` command.

## [v0.1.0](https://github.com/naacl2022-reproducibility-track/naacl-utils/releases/tag/v0.1.0) - 2021-12-08

### Added

- Added `naacl-utils` command line interface.
