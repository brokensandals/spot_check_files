# spot\_check\_files

This is a tool to help validate the integrity of data backups/exports.

- Checks recognized file types for errors, e.g. invalid json.
- Selects some files at random to show you samples of, e.g. an image of part of a PDF or HTML page.

## Usage

Install:

1. Install python3 and pip
2. `pip3 install spot_check_files`

Full command list and options can be seen in the [doc folder](doc/).

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
