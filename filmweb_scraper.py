from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from film import FilmwebFilm
from person import Person

def main():
  best_films = 'https://www.filmweb.pl/ranking/film'

  browser = webdriver.Firefox()
  browser.implicitly_wait(40)
  browser.get(best_films)
  browser.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]').click()

  film_list = browser.find_element(By.XPATH, '/html/body/div[5]/div[4]/div[2]/div/div[3]/section[1]/div[2]')

  for _ in range(0):
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
    films.append(get_film_from_link(browser, link))
    print(f'{i+1}/{len(links)}: {browser.title}')
  
  genre_names = set()
  director_links = set()
  creator_links = set()
  actor_links = set()

  for film in films:
    genre_names.add(film.genre)
    director_links.add(film.director_link)
    creator_links.add(film.writer_link)
    for role in film.roles:
      actor_links.add(role[1])
  actors = []
  directors = []
  writers = []

  browser.implicitly_wait(10)
  print("---ACTORS---")
  for i, actor_link in enumerate(actor_links):
    actor = get_person_from_link(browser, actor_link)
    if actor != None:
      actors.append(actor)
    print(f"{i+1}/{len(actor_links)}: {actors[-1]}")
  
  print("---DIRECTORS---")
  for i, director_link in enumerate(director_links):
    director = get_person_from_link(browser, director_link)
    if director != None:
      directors.append(director)
    print(f"{i+1}/{len(director_links)}: {directors[-1]}")
  
  print("---CREATORS---")
  for i, writer_link in enumerate(creator_links):
    writer = get_person_from_link(browser, writer_link)
    if writer != None:
      writers.append(writer)
    print(f"{i+1}/{len(creator_links)}: {writers[-1]}")
  
  genre_inserts(genre_names)
  director_inserts(directors)
  creators_inserts(writers)
  actors_inserts(actors)

  
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
    lines.append(f"\n({i+1}, '{director.first_name}', '{director.surname}', '{director.birth_date}', '{director.country}')" + ("," if i != len(directors)-1 else ";"))

  file = open('data/directors.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()

  
def creators_inserts(creators: list):
  lines = [
    'INSERT INTO scenarzysci (id_scenarzysty, imie, nazwisko, data_urodzenia, kraj_pochodzenia) VALUES'
  ]
  
  for i, creator in enumerate(creators):
    lines.append(f"\n({i+1}, '{creator.first_name}', '{creator.surname}', '{creator.birth_date}', '{creator.country}')" + ("," if i != len(creators)-1 else ";"))

  file = open('data/creators.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()
  
def actors_inserts(actors: list):
  lines = [
    'INSERT INTO aktorzy (id_aktora, imie, nazwisko, data_urodzenia, kraj_pochodzenia) VALUES'
  ]
  
  for i, actor in enumerate(actors):
    lines.append(f"\n({i+1}, '{actor.first_name}', '{actor.surname}', '{actor.birth_date}', '{actor.country}')" + ("," if i != len(actors)-1 else ";"))

  file = open('data/actors.sql', 'w', encoding='utf8')
  file.writelines(lines)
  file.close()

def get_film_from_link(browser: webdriver.Firefox , link: str) -> FilmwebFilm:
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

  return FilmwebFilm(title, date_published, duration_mins, country, description, genre, director_link, creator_link, roles)

def get_person_from_link(browser: webdriver.Firefox , link: str) -> Person:
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

  return Person(first_name, surname, birth_date, birth_place, link)


if __name__ == '__main__':
  main()
