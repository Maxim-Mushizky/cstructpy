# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0]

### Added

- Added the ability to check equality between subclasses of GenericStruct- allowing easier method to test data integrity
- Added exceptions file to handle the complex exceptions that might occur
- Added ability to use any primitive type apart for CHAR as an array, via "__class_getitem__" method
- Added ability to print the values in GenericStruct object

### Fixed

- Fixed not being able to compare GenericStruct objects directly via the '=' operator

## [0.1.0] - 2024-10-01

### First release