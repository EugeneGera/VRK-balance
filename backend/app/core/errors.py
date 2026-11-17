from typing import List, Optional, Union


class NotFoundError(Exception):
    def __init__(self, model: str, key: str):
        self.model = model
        self.key = key
        super().__init__(f"{model} with {key} not found")


class UploadFolderNotFoundException(Exception):
    def __init__(self, msg: str):
        super().__init__(f"Upload folder not found: {msg}")

class FileUploadException(Exception):
    def __init__(self, msg: str):
        super().__init__(f"File upload fail: {msg}")

class CalculationFailException(Exception):
    def __init__(self, msg: str):
        super().__init__(f"Exception occured during calculations: {msg}")

class IncorrectFileFormatException(Exception):
    def __init__(self, expected_formats: Optional[Union[str, List[str]]] = None):
        msg = f"Incorrect file format"
        if expected_formats:
            msg += f"\nExpected format(-s): {expected_formats}"
        super().__init__(msg)

class InvalidUploadTypeException(Exception):
    def __init__(self, msg: str):
        super().__init__(f"Invalid type of upload: {msg}")

class FileSavingException(Exception):
    def __init__(self, msg: str):
        super().__init__(f"Exception while saving file: {msg}")

class MissingFileException(Exception):
    def __init__(self):
        super().__init__(f"No file was uploaded")

class FileDeletionException(Exception):
    def __init__(self, file_names : Optional[List[str]] = None):
        super().__init__(f"Failed while deleting files: {file_names}")