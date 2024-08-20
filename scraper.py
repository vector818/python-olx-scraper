import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

# Definicja funkcji do pobierania treści ogłoszenia
def pobierz_tresc_ogloszenia(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        opis = soup.find('div', {'data-cy': 'ad_description'})
        if opis:
            return opis.find('div', class_='css-1t507yq').text
    return 'Nie udało się pobrać opisu.'

# URL strony z listą ogłoszeń
url = "https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/"
def przetwarzaj_strone(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Znajdź wszystkie ogłoszenia na liście
        ogloszenia = soup.select('div[data-cy="l-card"]')

        data = []

        for ogloszenie in ogloszenia:
            # Znajdź link do ogłoszenia
            link = ogloszenie.find('a', class_='css-rc5s2u')
            if link:
                url_ogloszenia = f'https://www.olx.pl/{link["href"]}'
                title = link.find('h6').text if link.find('h6') else 'Brak tytułu'
                print(f'Przetwarzanie: {url_ogloszenia}, Tytuł: {title}')
                cena = ogloszenie.find('p', {'data-testid': 'ad-price'}).text if ogloszenie.find('p', {'data-testid': 'ad-price'}) else 'Brak ceny'
                
                # Pobierz treść ogłoszenia
                tresc_ogloszenia = pobierz_tresc_ogloszenia(url_ogloszenia)
                
                # Dodaj dane do listy
                data.append({'Title': title, 'Treść ogłoszenia': tresc_ogloszenia, 'Cena': cena})

        # Utwórz ramkę danych pandas
        df = pd.DataFrame(data)
        return df
    else:
        print(f'Nie udało się pobrać strony. Kod odpowiedzi: {response.status_code}')

if __name__ == '__main__':
    # URL strony głównej z listą ogłoszeń
    url_base = 'https://www.olx.pl/nieruchomosci/garaze-parkingi/wynajem/warszawa/?search%5Bdistrict_id%5D=381'

    response = requests.get(url_base)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Znajdź maksymalny numer strony
    pagination = soup.find('ul', {'data-testid': 'pagination-list'})
    links = pagination.find_all('a', class_='css-1mi714g') if pagination else []
    max_page = max([int(link.text) for link in links if link.text.isdigit()], default=1)

    # Iteracja przez wszystkie strony i przetwarzanie
    dfs = []
    for page_number in range(1, max_page + 1):
        page_url = f"{url}?page={page_number}&search%5Bdistrict_id%5D=381"
        print(f'Przetwarzanie strony: {page_url}')
        dfs.append(przetwarzaj_strone(page_url))
    df_out = pd.concat(dfs, ignore_index=True)
    df_out.head()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'wynajem_garazy_warszawa_{timestamp}.csv'
    df_out.to_csv(filename, index=False)
