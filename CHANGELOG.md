# Changelog


## [0.6.3] - 2015-06-05
### Fixed
* `path-to-regexp` to `repath` in README


## [0.6.1] - 2015-06-05
### Added
* Reformatted `PATH_REGEXP` for easier reading
* Rewrote comments describing captured fields


## [0.6.0] - 2015-06-05
### Changed
* rename `path_to_pattern` to `pattern`
* rename `compile` to `template`

## [0.5.0] - 2015-06-04
### Removed
* `array_to_pattern`
* `string_to_pattern`

These functions are covered by `path_to_pattern` which already accepts these
types of values.


## [0.4.0] - 2015-06-02
### Removed
* `keys` argument
* `regxp_to_pattern` function (without the keys it does nothing useful)

### Changed
* rename `tokens_to_function` to `tokens_to_template`


## [0.2.0] - 2015-06-01
## Changed
* Options are passed as individual keyword arguments instead of a dictoinary

## 0.1.0 - 2015-06-01
### Added
* A module mostly compatible with original path-to-regexp project, except:
* Function names switched from camelCase to snake_case
* Module only generates regular expression patterns, not regex objects
* `keys` argument is not used, made redundant by named capture groups

[unreleased]: https://github.com/nickcoutsos/python-repath/compare/v0.6.3...HEAD
[0.6.3]: https://github.com/nickcoutsos/python-repath/compare/v0.6.1...v0.6.3
[0.6.1]: https://github.com/nickcoutsos/python-repath/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/nickcoutsos/python-repath/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/nickcoutsos/python-repath/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/nickcoutsos/python-repath/compare/v0.2.0...v0.4.0
[0.2.0]: https://github.com/nickcoutsos/python-repath/compare/v0.1.0...v0.2.0