from typing import Tuple

def pagecount(wordcount:int) -> float:
    """Returns the estimated number of pages the given wordcount would produce using industry standard calculations."""
    WORDS_PER_PAGE = 300
    return wordcount / WORDS_PER_PAGE

def reading_time(wordcount:int) -> Tuple[int, int, int]:
    """Returns a tuple of the form (hours, minutes, seconds) representing the time it would take an adult to read the specified wordcount."""
    # Words per minute reading rate:
    READING_WPM = 275
    (minutes, seconds) = divmod(wordcount, READING_WPM)
    (hours, minutes) = divmod(minutes, 60)
    seconds = (int)((seconds / READING_WPM) * 60)
    return (hours, minutes, seconds)

def reading_time_str(reading_time:Tuple[int, int, int]) -> str:
    """Returns a formatted string in the form of h:mm:ss for the supplied reading time tuple (hours, minutes, seconds)."""
    (hours, minutes, seconds) = reading_time
    return f'{hours}:{minutes:02}:{seconds:02}'