from importlib.resources import files

def _get_file(package: str, filename: str):
    return files(package).joinpath(filename).read_text(encoding="utf-8")

def load_text(package: str, filename: str) -> str:
    return _get_file(package, filename)

def load_word_set(package: str, filename: str) -> set[str]:
    return {
        line.strip()
        for line in _get_file(package, filename).splitlines()
        if line.strip()
    }