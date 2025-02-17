# import requests
# from bs4 import BeautifulSoup


# url_list = {}
# api_key = "ENTER YOUR API KEY HERE"


# def search_movies(query):
#     movies_list = []
#     movies_details = {}
#     website = BeautifulSoup(requests.get(f"https://185.53.88.104/?s={query.replace(' ', '+')}").text, "html.parser")
#     movies = website.find_all("a", {'class': 'ml-mask jt'})
#     for movie in movies:
#         if movie:
#             movies_details["id"] = f"link{movies.index(movie)}"
#             movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
#             url_list[movies_details["id"]] = movie['href']
#         movies_list.append(movies_details)
#         movies_details = {}
#     return movies_list


# def get_movie(query):
#     movie_details = {}
#     movie_page_link = BeautifulSoup(requests.get(f"{url_list[query]}").text, "html.parser")
#     if movie_page_link:
#         title = movie_page_link.find("div", {'class': 'mvic-desc'}).h3.text
#         movie_details["title"] = title
#         img = movie_page_link.find("div", {'class': 'mvic-thumb'})['data-bg']
#         movie_details["img"] = img
#         links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
#         final_links = {}
#         for i in links:
#             url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
#             response = requests.get(url)
#             link = response.json()
#             final_links[f"{i.text}"] = link['shortenedUrl']
#         movie_details["links"] = final_links
#     return movie_details


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url_list = {}

def search_movies(query):
    movies_list = []
    base_url = "https://hdhub4u.gy/"
    search_url = f"{base_url}/?s={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    try:
        response = requests.get(search_url, headers=headers, verify=False)
        response.raise_for_status()
        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        for idx, movie in enumerate(movies):
            if movie:
                movies_details = {
                    "id": f"link{idx}",
                    "title": movie.find("span", {'class': 'mli-info'}).get_text(strip=True)
                }
                movie_url = urljoin(base_url, movie['href'])
                url_list[movies_details["id"]] = movie_url
                movies_list.append(movies_details)
        
        return movies_list
    
    except Exception as e:
        print(f"Error in search_movies: {e}")
        return []

def get_movie(query):
    try:
        movie_url = url_list.get(query)
        if not movie_url:
            return {}
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(movie_url, headers=headers, verify=False)
        response.raise_for_status()
        movie_page = BeautifulSoup(response.text, "html.parser")
        
        title = movie_page.find("div", {'class': 'mvic-desc'}).h3.get_text(strip=True)
        img_tag = movie_page.find("div", {'class': 'mvic-thumb'}).img
        img = img_tag['src'] if img_tag else None
        
        links = {}
        for link in movie_page.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'}):
            links[link.get_text(strip=True)] = link['href']
        
        return {
            "title": title,
            "img": img,
            "links": links
        }
    
    except Exception as e:
        print(f"Error in get_movie: {e}")
        return {}
