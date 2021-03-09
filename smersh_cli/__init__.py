import importlib_metadata


try:
    __all__ = (
        "__title__",
        "__summary__",
        "__uri__",
        "__version__",
        "__author__",
        "__email__",
        "__license__",
    )

    metadata = importlib_metadata.metadata("smersh_cli")

    __title__ = metadata["name"]
    __summary__ = metadata["summary"]
    __uri__ = metadata["home-page"]
    __version__ = metadata["version"]
    __author__ = metadata["author"]
    __email__ = metadata["author-email"]
    __license__ = metadata["license"]
except importlib_metadata.PackageNotFoundError:
    pass
