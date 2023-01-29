from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from film import FilmwebFilm
from person import Person

def full_scrape():
  best_films = 'https://www.filmweb.pl/ranking/film'

  browser = webdriver.Firefox()
  browser.implicitly_wait(40)
  browser.get(best_films)
  browser.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]').click()

  film_list = browser.find_element(By.CLASS_NAME, 'rankingTypeSection__container')

  for _ in range(1):
    browser.execute_script(f'window.scrollTo(0, {film_list.location["y"] + film_list.size["height"]})')
    browser.execute_script(f'window.scrollBy(0, -100)')
    browser.execute_script(f'window.scrollBy(0, -100)')
    browser.execute_script(f'window.scrollBy(0, -100)')
    browser.execute_script(f'window.scrollBy(0, -100)')
    browser.execute_script(f'window.scrollBy(0, -100)')
    browser.execute_script(f'window.scrollBy(0, -100)')
    sleep(1)
    browser.execute_script(f'window.scrollBy(0, 100)')
    browser.execute_script(f'window.scrollBy(0, 100)')
    browser.execute_script(f'window.scrollBy(0, 100)')
    browser.execute_script(f'window.scrollBy(0, 100)')
    browser.execute_script(f'window.scrollBy(0, 100)')
    browser.execute_script(f'window.scrollBy(0, 100)')
    sleep(1)

  film_divs = film_list.find_elements(By.CLASS_NAME, 'rankingType')

  print(f'{len(film_divs)} films found')
  links = []
  for film in film_divs:
    anchor = film.find_element(By.TAG_NAME, 'a')
    links.append(anchor.get_attribute('href'))
  films = []
  # films.append(get_film_from_link(browser, links[0]))
  print("---FILMS---")
  for i, link in enumerate(links[:5]):
    films.append(get_film_from_link(browser, link, id=i+1))
    print(f'{i+1}/{len(links)}: {browser.title}')
  
  genre_names = set()
  director_links = set()
  creator_links = set()
  actor_links = set()

  for film in films:
    genre_names.add(film.genre)
    director_links.add(film.director_link)
    creator_links.add(film.writer_link)
    for role in film.roles[:3]:
      actor_links.add(role[1])
  actors = []
  directors = []
  writers = []

  browser.implicitly_wait(10)
  print("---ACTORS---")
  for i, actor_link in enumerate(actor_links):
    actor = get_person_from_link(browser, actor_link, id=i+1)
    if actor != None:
      actors.append(actor)
      print(f"{i+1}/{len(actor_links)}: {actors[-1]}")
  
  print("---DIRECTORS---")
  for i, director_link in enumerate(director_links):
    director = get_person_from_link(browser, director_link, id=i+1)
    if director != None:
      directors.append(director)
    print(f"{i+1}/{len(director_links)}: {directors[-1]}")
  
  print("---CREATORS---")
  for i, writer_link in enumerate(creator_links):
    writer = get_person_from_link(browser, writer_link, id=i+1)
    if writer != None:
      writers.append(writer)
    print(f"{i+1}/{len(creator_links)}: {writers[-1]}")
  
  print('---GENRE INSERTS---')
  genre_inserts(genre_names)
  print('---DIRECTOR INSERTS---')
  director_inserts(directors)
  print('---CREATOR INSERTS---')
  creators_inserts(writers)
  print('---ACTOR INSERTS---')
  actors_inserts(actors)
  print('---FILM INSERTS---')
  film_inserts(films, directors, writers)
  print('---ROLE INSERTS---')
  role_inserts(films, actors)

  get_example_data_together()

def get_example_data_together():
  file_names = [
    "genres",
    "creators",
    "directors",
    "actors",
    "films",
    "roles"
  ]

  output_lines = []

  for name in file_names:
    output_lines.append(f"\n\n---{name}\n\n")
    file = open(f"data/{name}.sql", "r", encoding='utf8')
    lines = file.readlines()
    file.close()
    output_lines.extend(lines)
  file = open("data/example_data.sql", "w", encoding="utf8")
  file.writelines(output_lines)
  file.close()


def film_inserts(films: list[FilmwebFilm], directors: list[Person], writers: list[Person]):
  lines = [
    "INSERT INTO filmy (id_filmu, tytul, data_wydania, id_rezysera, id_scenarzysty, gatunek, czas_trwania, kraj_produkcji, opis) VALUES"
  ]
  for i, film in enumerate(films):
    can_be_inserted = True
    director = [d for d in directors if d.filmweb_link == film.director_link]
    if len(director) > 0:
      director = director[0].id
    else:
      can_be_inserted = False
      print(f"You have to insert director and their id manually for film: {film.title}, director link: {film.director_link}")
      print(film)
    writer = [w for w in writers if w.filmweb_link == film.writer_link]
    if len(writer) > 0:
      writer = writer[0].id
    else:
      can_be_inserted = False
      print(f"You have to insert writer and their id manually for film: {film.title}, writer link: {film.writer_link}")
    if not can_be_inserted:
      continue
    lines.append(f"\n({film.id}, '{film.title}', '{film.premiere_date}', {director}, {writer}, '{film.genre}', {film.length}, '{film.country}', '{film.description}')" + ("," if i != len(films)-1 else ";"))
  file = open('data/films.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close

def role_inserts(films: list[FilmwebFilm], actors: list[Person]):
  lines = [
    'INSERT INTO role (nazwa_roli, id_aktora, id_filmu) VALUES'
  ]

  for film in films:
    for role in film.roles:
      actor = [a for a in actors if a.filmweb_link == role[1]]
      if len(actor) > 0:
        actor = actor[0].id
      else:
        print(f"Actor with link '{role[1]}' not found for film: ")
        print(film.title)
        print("Insert them manually")
        continue
      lines.append(f"\n('{role[0]}', {actor}, {film.id}),")
  file = open("data/roles.sql", "w", encoding="utf8")
  file.writelines(lines)
  file.close()
  print("Roles saved, remember to change last comma for a semi-colon (',' -> ';')")  


def genre_inserts(names: set):
  lines = [
    'INSERT INTO gatunki (nazwa_gatunku, opis_gatunku) VALUES'
  ]
  
  for i, name in enumerate(names):
    lines.append(f"\n('{name}', '')" + ("," if i != len(names)-1 else ";"))

  file = open('data/genres.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()

def director_inserts(directors: list):
  lines = [
    'INSERT INTO rezyserowie (id_rezysera, imie, nazwisko, data_urodzenia, kraj_pochodzenia) VALUES'
  ]
  
  for i, director in enumerate(directors):
    lines.append(f"\n({director.id}, '{director.first_name}', '{director.surname}', '{director.birth_date}', '{director.country}')" + ("," if i != len(directors)-1 else ";"))

  file = open('data/directors.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()

  
def creators_inserts(creators: list):
  lines = [
    'INSERT INTO scenarzysci (id_scenarzysty, imie, nazwisko, data_urodzenia, kraj_pochodzenia) VALUES'
  ]
  
  for i, creator in enumerate(creators):
    lines.append(f"\n({creator.id}, '{creator.first_name}', '{creator.surname}', '{creator.birth_date}', '{creator.country}')" + ("," if i != len(creators)-1 else ";"))

  file = open('data/creators.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()
  
def actors_inserts(actors: list):
  lines = [
    'INSERT INTO aktorzy (id_aktora, imie, nazwisko, data_urodzenia, kraj_pochodzenia) VALUES'
  ]
  
  for i, actor in enumerate(actors):
    lines.append(f"\n({actor.id}, '{actor.first_name}', '{actor.surname}', '{actor.birth_date}', '{actor.country}')" + ("," if i != len(actors)-1 else ";"))

  file = open('data/actors.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()

def get_film_from_link(browser: webdriver.Firefox , link: str, id: int) -> FilmwebFilm:
  browser.get(link)
  
  title_class = "filmCoverSection__title"
  date_published_itemprop = "datePublished" #`content` has the date in a sensible format
  genre_itemprop = "genre"
  duration_class = "filmCoverSection__duration" #`data-duration` has minutes
  description_itemprop = "description"

  title = browser.find_element(By.CLASS_NAME, title_class).text
  date_published = browser.find_element(By.XPATH, f"//span[contains(@itemprop, '{date_published_itemprop}')]").get_attribute("content")
  genre = browser.find_element(By.XPATH, f"//div[contains(@itemprop, '{genre_itemprop}')]/span/a").text
  duration_mins = browser.find_element(By.CLASS_NAME, duration_class).get_attribute("data-duration")
  description = browser.find_element(By.XPATH, f"//span[contains(@itemprop, '{description_itemprop}')]").text
  # country = browser.find_element(By.XPATH, "/html/body/div[5]/div[3]/div[2]/div/div[2]/section/div/div/div[4]/div[4]/span/a").text
  # country = browser.find_element(By.XPATH, "/html/body/div[5]/div[4]/div[2]/div/div[2]/section/div/div/div[4]/div[4]/span/a").text
  country = browser.find_element(By.XPATH, "//*/text()[.='produkcja']/following::div").text

  director_link = browser.find_element(By.XPATH, f"//a[contains(@itemprop, 'director')]").get_attribute("href")
  creator_link = browser.find_element(By.XPATH, f"//a[contains(@itemprop, 'creator')]").get_attribute("href")

  roles = []
  actors_ui_list = browser.find_element(By.CLASS_NAME, "crs__wrapper")

  actors = actors_ui_list.find_elements(By.CLASS_NAME, "SimplePoster")

  for actor in actors:
    actor_link = actor.find_element(By.CLASS_NAME, "simplePoster__title").get_attribute("href")
    role_name = actor.find_element(By.CLASS_NAME, "simplePoster__character").text
    roles.append((role_name, actor_link))

  return FilmwebFilm(id, title, date_published, duration_mins, country, description, genre, director_link, creator_link, roles, link)

def get_person_from_link(browser: webdriver.Firefox , link: str, id: int) -> Person:
  browser.get(link)
  name = ""
  birth_date = ""
  birth_place = ""
  try:
    name = browser.find_element(By.XPATH, "//span[contains(@itemprop, 'name')]").text.title()
    birth_date = browser.find_element(By.XPATH, "//span[contains(@itemprop, 'birthDate')]").get_attribute('content')
    birth_place = browser.find_element(By.XPATH, "//span[contains(@itemprop, 'birthPlace')]").text.title()
  except:
    print("not enough data :(")
    return None
  name = name.split(" ")
  first_name = name[0]
  surname = name[-2]
  birth_place = birth_place.split(', ')[-1]

  return Person(id, first_name, surname, birth_date, birth_place, link)


if __name__ == '__main__':
  # full_scrape()
  get_example_data_together()
