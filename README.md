# spot\_check\_files

This is a tool to help validate the integrity of data backups/exports.

- Checks recognized file types for errors, e.g. invalid json.
- Selects some files at random to show you thumbnails of.

## Usage

Install:

1. Install python3 and pip
2. `pip3 install spot_check_files[imgcat]`
    - imgcat is optional and enables support for displaying thumbnails in iTerm2 on OS X

Run:

```bash
spot_check_files PATH
```

This will output basic stats and any problems the tool detects in the given files/directories.
If you're using iTerm2 on Mac, it will also show thumbnails of a few randomly-selected files.

The full list of options can be seen in the [doc folder](doc/).

This tool can also be used programmatically.
The main entry point for the library is [spot_check_files.checker.Checker](src/spot_check_files/checker.py).

## Supported file types

File types are currently recognized only by file extension.

<table>
    <thead>
        <tr>
            <th>Type</th>
            <th>Support</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                <ul>
                    <li><code>.tar</code></li>
                    <li><code>.tar.bz2</code></li>
                    <li><code>.tar.gz</code></li>
                    <li><code>.tar.xz</code></li>
                    <li><code>.tbz</code></li>
                    <li><code>.tgz</code></li>
                    <li><code>.txz</code></li>
                    <li><code>.zip</code></li>
                </ul>
            </td>
            <td>Recursively checks all the files in the archive (including other archives)</td>
        </tr>
        <tr>
            <td><code>.json</code></td>
            <td>Checks that the json can be parsed</td>
        </tr>
        <tr>
            <td><code>.xml</code></td>
            <td>Checks that the xml can be parsed</td>
        </tr>
        <tr>
            <td>anything supported by OS X Quick Look (HTML, Office docs, ...)</td>
            <td>OS X ONLY: generates thumbnails using Quick Look. This greatly increases the number of supported file types. However, it's slow. See the <code>-q</code> command line option if you wish to partially or fully disable it.</td>
        </tr>
    </tbody>
</table>

## Development

Setup:

1. Install python3 and pip
2. Clone the repo
3. I recommend creating a venv:
    ```bash
    cd spot_check_files
    python3 -m venv venv
    source venv/bin/activate
    ```
4. Install dependencies:
    ```bash
   pip install .
   pip install -r requirements-dev.txt
    ```

To run tests:

```bash
PYTHONPATH=src pytest
```

(Overriding PYTHONPATH as shown ensures the tests run against the code in the src/ directory rather than the installed copy of the package.)

To run the CLI:

```bash
PYTHONPATH=src python -m spot_check_files ...
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/brokensandals/spot_check_files.

## License

This is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

This package includes and uses a copy of the [Monoid](https://github.com/larsenwork/monoid) font, which is also MIT-licensed.
