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

url_list = {}

def search_movies(query):
    try:
        movies_list = []
        # Add headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Make the request with proper timeout
        response = requests.get(
            f"https://185.53.88.104/?s={query.replace(' ', '+')}",
            headers=headers,
            timeout=10
        )
        
        website = BeautifulSoup(response.text, "html.parser")
        movies = website.find_all("a", {'class': 'ml-mask jt'})
        
        for movie in movies:
            try:
                if movie and movie.find("span", {'class': 'mli-info'}):
                    movies_details = {
                        "id": f"link{len(movies_list)}",
                        "title": movie.find("span", {'class': 'mli-info'}).text.strip()
                    }
                    url_list[movies_details["id"]] = movie['href']
                    movies_list.append(movies_details)
            except Exception as e:
                print(f"Error processing movie: {str(e)}")
                continue
                
        return movies_list
    except Exception as e:
        print(f"Error in search_movies: {str(e)}")
        return []

def get_movie(query):
    try:
        if query not in url_list:
            return None
            
        movie_details = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url_list[query], headers=headers, timeout=10)
        movie_page_link = BeautifulSoup(response.text, "html.parser")
        
        if movie_page_link:
            desc_div = movie_page_link.find("div", {'class': 'mvic-desc'})
            if desc_div and desc_div.h3:
                movie_details["title"] = desc_div.h3.text.strip()
            
            thumb_div = movie_page_link.find("div", {'class': 'mvic-thumb'})
            if thumb_div and 'data-bg' in thumb_div.attrs:
                movie_details["img"] = thumb_div['data-bg']
            
            links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
            final_links = {}
            
            for link in links:
                if link.text and link.get('href'):
                    final_links[link.text.strip()] = link['href']
            
            movie_details["links"] = final_links
            return movie_details
            
    except Exception as e:
        print(f"Error in get_movie: {str(e)}")
        return None
