from dataclasses import dataclass
from datetime import date

@dataclass
class FilmwebFilm:
  id: int

  title: str
  premiere_date: date
  length: int
  country: str
  description: str
  genre: str

  director_link: str
  writer_link: str
  roles: list #(role_name, actor_link)

  filmweb_link: str
