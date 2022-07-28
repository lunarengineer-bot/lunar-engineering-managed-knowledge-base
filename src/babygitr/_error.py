"""Defines exceptions used in BabyGitr.

This is used to localize when an error is within the BabyGitr code.
"""


class BabyGitrBaseException(Exception):
    """Serves as a base exception for BabyGitr."""

    def __init__(self, message=""):
        self.message = f"""BabyGitrBaseException\n{message}"""
        super().__init__(self.message)
