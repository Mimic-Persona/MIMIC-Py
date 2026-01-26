import os


def system_say(text: str):
    """
    Uses the system's text-to-speech functionality to speak the provided text.
    :param text: The text to be spoken.
    :return: None
    """
    os.system(f'say {text}')