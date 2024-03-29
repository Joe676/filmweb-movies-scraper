from dataclasses import dataclass
from datetime import date

@dataclass
class Person:
  id: int
  first_name: str
  surname: str
  birth_date: date
  country: str

  filmweb_link: str