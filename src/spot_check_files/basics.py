from spot_check_files.checker import Checker, CheckRequest, CheckResult


class PlaintextChecker(Checker):
    """Checks a plaintext file for encoding problems.

    This will read the input as a text file, relying on Python's default
    behavior to select the encoding. The checker will mark the file as
    recognized as long as it is able to open it. It will attempt to read
    the entire file and add an error if it cannot decode it.
    """
    def __str__(self):
        return 'PlaintextChecker'

    def check(self, req: CheckRequest) -> CheckResult:
        result = CheckResult()
        try:
            with open(req.realpath, 'r') as file:
                result.recognizer = self
                for line in file:
                    pass
        except ValueError as e:
            result.errors.append(e)
        return result
