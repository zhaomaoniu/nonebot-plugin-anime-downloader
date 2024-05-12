class TorrentExistsError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"TorrentExistsError: {self.message}"

    def __repr__(self):
        return f"TorrentExistsError: {self.message}"


class TorrentUnexistsError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"TorrentUnexistsError: {self.message}"

    def __repr__(self):
        return f"TorrentUnexistsError: {self.message}"
