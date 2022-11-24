"""
lotto/drawings.py
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List

import arrow
import requests


class DrawingType(Enum):
    MEGA_MILLIONS = "mega_millions"
    POWERBALL = "powerball"


class LotteryDrawing(ABC):
    def __init__(
        self,
        start_date: str,
        end_date: str,
    ) -> None:
        """Constructor for base class

        Args:
            start_date (str): start of drawings to query
            end_date (str): end of drawings to query
        """
        super().__init__()
        self._start_date = arrow.get(start_date)
        self._end_date = arrow.get(end_date)

    @property
    def start_date(self) -> arrow.Arrow:
        return self._start_date

    @property
    def end_date(self) -> arrow.Arrow:
        return self._end_date

    @abstractmethod
    def get_drawings(self) -> Dict[str, List[int]]:
        """Get a message containing hit information"""


class MegaMillionsDrawing(LotteryDrawing):
    """
    Source: https://data.ny.gov/Government-Finance/
        Lottery-Mega-Millions-Winning-Numbers-Beginning-20/5xaw-6ayf

    [{"draw_date":"2022-11-22T00:00:00.000",
        "winning_numbers":"13 23 24 25 43","mega_ball":"02",
        "multiplier":"03"}, ...]
    """

    URL = "https://data.ny.gov/resource/5xaw-6ayf.json"

    def __init__(
        self,
        start_date: str,
        end_date: str,
    ) -> None:
        super(MegaMillionsDrawing, self).__init__(start_date, end_date)

    def get_drawings(self) -> Dict[str, List[int]]:
        response = requests.get(MegaMillionsDrawing.URL)
        drawings = response.json()
        relevant_drawings = {}
        for drawing in drawings:
            draw_date = drawing["draw_date"][:10]
            if not self.start_date <= arrow.get(draw_date) <= self.end_date:
                continue
            relevant_drawings[draw_date] = [
                int(x) for x in drawing["winning_numbers"].split(" ")
            ] + [int(drawing["mega_ball"])]
        return relevant_drawings


class PowerballDrawing(LotteryDrawing):
    """
    Source: https://data.ny.gov/Government-Finance/
        Lottery-Powerball-Winning-Numbers-Beginning-2010/d6yy-54nr

    [{"draw_date":"2022-11-21T00:00:00.000",
    "winning_numbers":"01 06 40 51 67 02","multiplier":"2"} ...]
    """

    URL = "https://data.ny.gov/resource/d6yy-54nr.json"

    def __init__(
        self,
        start_date: str,
        end_date: str,
    ) -> None:
        super(PowerballDrawing, self).__init__(start_date, end_date)

    def get_drawings(self) -> Dict[str, List[int]]:
        response = requests.get(PowerballDrawing.URL)
        drawings = response.json()
        relevant_drawings = {}
        for drawing in drawings:
            draw_date = drawing["draw_date"][:10]
            if not self.start_date <= arrow.get(draw_date) <= self.end_date:
                continue
            relevant_drawings[draw_date] = [
                int(x) for x in drawing["winning_numbers"].split(" ")
            ]
        return relevant_drawings


class DrawingLoader:
    @staticmethod
    def load_drawing(
        lotto_name: str,
        start_date: str,
        end_date: str,
    ) -> LotteryDrawing:

        if DrawingType(lotto_name) == DrawingType.MEGA_MILLIONS:
            return MegaMillionsDrawing(start_date, end_date)
        elif DrawingType(lotto_name) == DrawingType.POWERBALL:
            return PowerballDrawing(
                start_date,
                end_date,
            )
        raise ValueError(f"Unknown lotto_name {lotto_name}")
