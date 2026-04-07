'''Meeting class
Author: Sunny Lin
Editors: 
Last modified: Apr 6, 26
'''

class Meeting:
    _title: str
    _time: float
    _description: str
    _participants: list[str]
    _labels: list[str]


    def __init__(self,
        title: str,
        time: float,
        description: str = '',
        participants: list[str] = [],
        labels: list[str] = [],
    ) -> None:
        self._title = title
        self._time = time
        self._description = description
        self._participants = participants
        self._labels = labels
    
    @classmethod
    def from_file(cls, entry_data: dict):
        return cls(
            entry_data['title'],
            entry_data['time'],
            entry_data['description'],
            entry_data['participants'],
            entry_data['labels'],
        )
    
    # Getters:
    def get_title(self) -> str: return self._title
    def get_time(self) -> float: return self._time
    def get_description(self) -> str: return self._description
    def get_participants(self) -> list[str]: return self._participants
    def get_labels(self) -> list[str]: return self._labels

    # Setters:
    def set_title(self, title: str) -> None: self._title = title
    def set_time(self, time: float) -> None: self._time = time
    def set_description(self, description: str) -> None: self._description = description
    def set_participants(self, participants: list[str]) -> None: self._participants = participants
    def set_labels(self, labels: list[str]) -> None: self._labels = labels
