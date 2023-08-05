def get_dictator_version():
    """
    Get latest dictator version

    Version is generated during the build process
    from the latest git tag and saved to version.txt
    """
    try:
        with open("version.txt", "r") as file:
            return file.read()

    except FileNotFoundError:
        return "Unknown"
