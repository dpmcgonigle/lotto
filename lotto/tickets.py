"""
lotto/tickets.py
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

import arrow


class LottoType(Enum):
    MEGA_MILLIONS = "mega_millions"
    POWERBALL = "powerball"


class LotteryTicket(ABC):
    def __init__(
        self,
        start_date: str,
        end_date: str,
        numbers: List[int],
        ticket_id: Optional[int] = None,
    ) -> None:
        """Constructor for base class

        Args:
            start_date (str): start of ticket
            end_date (str): end of ticket
            numbers (List[int]): Lottery numbers
            ticket_id (int, optional): id in database
        """
        super().__init__()
        self._start_date = arrow.get(start_date)
        self._end_date = arrow.get(end_date)
        self._numbers = numbers
        self._ticket_id = ticket_id

    @property
    def start_date(self) -> arrow.Arrow:
        return self._start_date

    @property
    def end_date(self) -> arrow.Arrow:
        return self._end_date

    @property
    def numbers(self) -> List[int]:
        return self._numbers

    @property
    def ticket_id(self) -> Optional[int]:
        return self._ticket_id

    @abstractmethod
    def check_winnings(self, drawing_date: str, winning_numbers: List[int]) -> str:
        """Get a message containing winnings information"""

    @property
    @abstractmethod
    def lotto_type(self) -> LottoType:
        raise NotImplementedError()


class MegaMillionsTicket(LotteryTicket):
    LOTTO_TYPE = LottoType.MEGA_MILLIONS

    def __init__(
        self,
        start_date: str,
        end_date: str,
        numbers: List[int],
        ticket_id: Optional[int] = None,
    ) -> None:
        super(MegaMillionsTicket, self).__init__(
            start_date, end_date, numbers, ticket_id=ticket_id
        )
        assert len(self._numbers), f"Expected 6, got {len(self._numbers)}"
        self._lotto_type = LottoType.MEGA_MILLIONS

    def check_winnings(self, drawing_date: str, winning_numbers: List[int]) -> str:
        """Get a message containing winnings information"""
        mb = winning_numbers[-1] == self.numbers[-1]
        matches = 0
        for winning_number in winning_numbers[:-1]:
            if winning_number in self._numbers[:-1]:
                matches += 1

        winnings: int
        if mb:
            winnings = {0: 2, 1: 4, 2: 10, 3: 200, 4: 10000, 5: 1000000}[matches]
        else:
            winnings = {0: 0, 1: 0, 2: 0, 3: 10, 4: 500, 5: 1000000}[matches]
        return f"{drawing_date} : MegaMillions ticket {self.numbers}\n \
            winning_numbers {winning_numbers}\n \
            hits: {matches}, megaball {mb}\n \
            winnings: ${winnings} \n\n"

    @property
    def lotto_type(self) -> LottoType:
        return MegaMillionsTicket.LOTTO_TYPE


class PowerballTicket(LotteryTicket):
    LOTTO_TYPE = LottoType.POWERBALL

    def __init__(
        self,
        start_date: str,
        end_date: str,
        numbers: List[int],
        ticket_id: Optional[int] = None,
    ) -> None:
        super(PowerballTicket, self).__init__(
            start_date, end_date, numbers, ticket_id=ticket_id
        )
        assert len(self._numbers), f"Expected 6, got {len(self._numbers)}"

    def check_winnings(self, drawing_date: str, winning_numbers: List[int]) -> str:
        """Get a message containing winnings information"""
        pb = winning_numbers[-1] == self.numbers[-1]
        matches = 0
        for winning_number in winning_numbers[:-1]:
            if winning_number in self._numbers[:-1]:
                matches += 1

        winnings: int
        if pb:
            winnings = {0: 4, 1: 4, 2: 7, 3: 100, 4: 50000, 5: 1000000}[matches]
        else:
            winnings = {0: 0, 1: 0, 2: 0, 3: 7, 4: 100, 5: 1000000}[matches]
        return f"{drawing_date} : Powerball ticket {self.numbers}\n \
            winning_numbers {winning_numbers}\n \
            hits: {matches}, powerball {pb}\n \
            winnings: ${winnings} \n\n"

    @property
    def lotto_type(self) -> LottoType:
        return PowerballTicket.LOTTO_TYPE


class TicketLoader:
    @staticmethod
    def load_ticket(
        lotto_name: str,
        start_date: str,
        end_date: str,
        numbers: List[int],
        ticket_id: Optional[int] = None,
    ) -> LotteryTicket:

        if LottoType(lotto_name) == LottoType.MEGA_MILLIONS:
            return MegaMillionsTicket(
                start_date, end_date, numbers, ticket_id=ticket_id
            )
        elif LottoType(lotto_name) == LottoType.POWERBALL:
            return PowerballTicket(start_date, end_date, numbers, ticket_id=ticket_id)
        raise ValueError(f"Unknown lotto_name {lotto_name}")
