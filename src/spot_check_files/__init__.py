"""A tool for validating and gathering statistics on a set of files.

The cli module implements the command-line interface. It inspects files
using checker.CheckerRunner (which uses Checkers from the archives,
basics, filenames, and quicklook modules) and displays results using
report.CheckReport.
"""