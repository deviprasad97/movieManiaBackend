from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup, NavigableString
import re
import json
import handlers.BluRayGetMediaReleaseDataHandler as blu_ray_handler

app = Flask(__name__)

headers = {
  'Accept': '*/*',
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Cookie': 'bblastvisit=1692197419; bblastactivity=0; firstview=1; search_section=theatrical',
  'DNT': '1',
  'Origin': 'https://www.blu-ray.com',
  'Referer': 'https://www.blu-ray.com/Star-Wars-Episode-II-Attack-of-the-Clones/20800/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"'
}
def configure_blu_ray_routes(app):
    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Movie or TV Series name is required'}), 400
        
        movies = search_helper(query=query)
        return jsonify({'movies': movies})

    @app.route('/getMovieReleases', methods=['GET'])
    def get_movie_releases():
        movie_id = request.args.get('id')
        if not movie_id:
            return jsonify({'error': 'Movie ID is required'}), 400

        releases = get_movie_releases_helper(movie_id=movie_id)

        return jsonify({'releases': releases})

    @app.route('/getMovieReleasesByQuery', methods=['GET'])
    def get_movie_releases_by_query():
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Movie or TV Series name is required'}), 400

        movies = search_helper(query=query)
        if len(movies) > 0:
            movie_id = movies[0]['id']
        else:
            return jsonify({'error': 'No matches found'}), 400
        releases = get_movie_releases_helper(movie_id=movie_id)

        return jsonify({'releases': releases})

    @app.route('/list4KMovies', methods=['GET'])
    def list_4k_movies():
        page_number = request.args.get('page', 0)
        url = f'https://www.blu-ray.com/movies/search.php?action=search&ultrahd=1&sortby=title&page={page_number}'

        # Make GET request
        response = requests.get(url, headers=headers)
        html_content = response.text

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract movie information
        movies = []
        seen_movies = set()
        for div in soup.find_all('div', style=lambda value: value and 'display: inline-block' in value):
            movie_info = {}
            a_tag = div.find('a', class_='hoverlink')
            if a_tag:
                movie_info['title'] = a_tag.get('title', '')
                movie_info['url'] = a_tag.get('href', '')
                movie_info['id'] = a_tag.get('data-productid', '')

                img_tag = a_tag.find('img', class_='cover')
                if img_tag:
                    movie_info['image_url'] = img_tag.get('src', '')
                if movie_info['id'] in seen_movies:
                    continue
                else:
                    seen_movies.add(movie_info['id'])
                movies.append(movie_info)

        return jsonify({'movies': movies})

    @app.route('/listBluRayMovies', methods=['GET'])
    def list_blu_ray_movies():
        page_number = request.args.get('page', 0)
        url = f'https://www.blu-ray.com/movies/movies.php?show=newreleases&page={page_number}'

        # Make GET request
        response = requests.get(url, headers=headers)
        html_content = response.text

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract movie information
        movies = {}
        current_date = None
        seen_movies = set()
        for div in soup.find_all('div', style=lambda value: value and 'display: inline-block' in value):
            if div.find_previous_sibling('h3'):
                current_date = div.find_previous_sibling('h3').get_text(strip=True)
            if not current_date:
                continue
            if current_date not in movies:
                movies[current_date] = []

            movie_info = {}
            a_tag = div.find('a', class_='hoverlink')
            if a_tag:
                movie_info['title'] = a_tag.get('title', '')
                movie_info['url'] = a_tag.get('href', '')
                movie_info['id'] = a_tag.get('data-productid', '')

                img_tag = a_tag.find('img', class_='cover')
                if img_tag:
                    movie_info['image_url'] = img_tag.get('src', '')
                
                if movie_info['id'] in seen_movies:
                    continue
                else:
                    seen_movies.add(movie_info['id'])

                movies[current_date].append(movie_info)
        return jsonify({'movies': movies})


    def search_helper(query):
        # External URL and POST data
        url = 'https://www.blu-ray.com/search/quicksearch.php'
        post_data = f"section=theatrical&userid=-1&country=US&keyword={query}"

        # Make POST request
        response = requests.post(url, data=post_data, headers=headers)
        html_content = response.text
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract script content
        script_content = soup.find('script', text=re.compile('var ids = new Array'))
        if not script_content:
            return jsonify({'error': 'Data not found'}), 404
        

        # Extract data from the script
        ids_str = re.search("var ids = new Array\((.*?)\);", script_content.string).group(1)
        urls_str = re.search("var urls = new Array\((.*?)\);", script_content.string).group(1)
        images_str = re.search("var images = new Array\((.*?)\);", script_content.string).group(1)
        ratings_str = re.search("var ratings = new Array\((.*?)\);", script_content.string).group(1)

        ids_list = [id.strip("'") for id in ids_str.split(', ')]
        ulrs_list = [url.strip("'") for url in urls_str.split(', ')]
        images_list = [image.strip("'") for image in images_str.split(', ')]
        ratings_list = [rating.strip("'") for rating in ratings_str.split(', ')]

        # Convert to Python lists
        try:
            ids = [int(id) for id in ids_list]
            urls = [str(url) for url in ulrs_list]
            images = [str(image) for image in images_list]
            ratings = [str(rating) for rating in ratings_list]
        except json.JSONDecodeError as e:
            return jsonify({'error': f'JSON decoding error: {e}'}), 500

        # Extract movie names
        movie_elements = soup.find_all('li', id=re.compile('match\d+'))
        movie_names = []
        for element in movie_elements:
            # Find the span element and extract its text
            span_text = element.find('span').get_text(strip=True) if element.find('span') else ''
            # Get the text of the entire li element
            full_text = element.get_text(strip=True)
            # Replace or remove the span text from the full text
            movie_name = full_text.replace(span_text, '').strip()
            movie_names.append(movie_name)
        # Construct response data
        movies = []
        for i in range(len(movie_names)):
            movie = {
                'name': movie_names[i],
                'id': ids[i],
                'url': urls[i],
                'image': images[i],
                'rating': ratings[i]
            }
            movies.append(movie)
        return movies

    def get_movie_releases_helper(movie_id):
        # URL with the movie ID
        url = f'https://www.blu-ray.com/products/menu_ajax.php?p={movie_id}&c=20&action=showreleases'

        # Make GET request
        response = requests.get(url, headers=headers)
        html_content = response.text

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract release information
        releases = []
        seen_release = set()
        release_counter = 1
        print(html_content)
        for h2_tag in soup.find_all('h2', class_='oswaldcollection'):
            release_type = h2_tag.get_text(strip=True)
            div_container = h2_tag.find_next_sibling('div')
            
            for div in div_container.find_all('div', style=True):
                release_info = {}
                release_info['type'] = release_type
                img_tag = div.find('img', class_='cover')
                release_info['image'] = img_tag['src'] if img_tag else None

                a_tag = div.find('a', class_='hoverlink')
                release_info['release_url'] = a_tag['href'] if a_tag else None
                release_info['release_title'] = a_tag['title'] if a_tag else None
                price_tag = div.find('b')
                release_info['price'] = price_tag.get_text(strip=True) if price_tag else None
                release_info['key'] = str(release_counter)
                if release_info['image'] or release_info['release_url']:
                    if release_info['image'] in seen_release or release_info['release_url'] in seen_release:
                        continue
                    else:
                        seen_release.add(release_info['image'])
                        seen_release.add(release_info['release_url'])
                release_counter += 1
                releases.append(release_info)
        return releases

    @app.route('/searchUPC', methods=['GET'])
    def search_upc():
        upc = request.args.get('upc')
        if not upc:
            return jsonify({'error': 'UPC is required'}), 400
        
        movie_data = search_upc_helper(upc)
        print(movie_data)
        if movie_data:
            return jsonify(movie_data)
        
        return jsonify({'error': 'No matching data found'}), 404

    def search_upc_helper(upc):
        # URL and POST data
        url = 'https://www.blu-ray.com/search/quicksearch.php'
        post_data = f"userid=-1&country=US&keyword={upc}"

        # Make POST request
        try:
            response = requests.post(url, data=post_data, headers=headers)
            html_content = response.text
        except Exception as e:
            return None

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract relevant information
        script_content = soup.find('script', text=re.compile('var ids = new Array'))
        if not script_content:
            return None

        ids = re.search("var ids = new Array\((.*?)\);", script_content.string).group(1).strip("'").split("', '")
        urls = re.search("var urls = new Array\((.*?)\);", script_content.string).group(1).strip("'").split("', '")
        images = re.search("var images = new Array\((.*?)\);", script_content.string).group(1).strip("'").split("', '")
        release_type = ""
        if '4K-Blu-ray' in urls[0]:
            release_type = "4K Blu-ray"
        elif 'Blu-ray' in urls[0]:
            release_type = "Blu-ray" 
        elif 'DVD' in urls[0]:
            release_type = "DVD" 


        li_element = soup.find('li', id='match0')
        if li_element:
            # Separate the release date and title
            date_span = li_element.find('span')
            release_date = date_span.get_text(strip=True) if date_span else ''
            title = li_element.get_text(strip=True).replace(release_date, '').strip()

            return {
                'title': title,
                'release_url': urls[0],
                'release_id': ids[0],
                'id': urls[0].split('/')[-2],
                'upc': upc,
                'image_url': images[0],
                'media_release_date': release_date,
                'release_type': release_type
            }
        return None
    

    @app.route('/getMediaReleaseData', methods=['POST'])
    def get_media_release_data():
        data = request.get_json()
        data_url = data.get('release_url')

        if not data_url:
            return jsonify({'error': 'release_url is required'}), 400

        response = requests.get(data_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        genres = [genre.get_text(strip=True) for genre in soup.select('.genreappeal a')]
        images = {}
        for image_type in ['front', 'back', 'slip', 'slipback']:
            if soup.find(id=f'large{image_type}image_overlay'):
                image_id = data_url.split('/')[-2]  # Assuming the ID is part of the URL
                images[image_type] = f"https://images.static-bluray.com/movies/covers/{image_id}_{image_type}.jpg"

        video_details = blu_ray_handler.extract_text(soup=soup, text='Video')

        # Audio details extraction
        audio_details = []
        audio_section = soup.find(id='shortaudio')
        if audio_section:
            for line in audio_section.stripped_strings:
                audio_details.append(line)

        # Subtitles extraction
        subtitles = []
        subtitles_section = soup.find(id='shortsubs')
        if subtitles_section:
            subtitles = [sub.strip() for sub in subtitles_section.text.split(',')]
        imdb_link = soup.find('a', id="imdb_icon")['href']
        imdb_id = re.search(r'/title/(tt\d+)/', imdb_link).group(1)
        # Discs details extraction
        discs_details = {
            'Types': blu_ray_handler.extract_text(soup, 'Discs'),
        }

        digital_details = {
            'AvailableOn': blu_ray_handler.extract_text(soup, 'Digital')
        }

        playback_details = blu_ray_handler.extract_text(soup, 'Playback')
        print(blu_ray_handler.extract_release_info(soup))

        response_data = {
            'Movie': {
                'Title': 'Deadpool 4K',
                'Format': 'Blu-ray',
                'Genres': genres,
                'Images': images
            },
            'Video': video_details,
            'Audio': audio_details,
            'Subtitles': subtitles,
            'Discs': discs_details,
            'Digital': digital_details,
            'Playback': playback_details,
            'Packaging': blu_ray_handler.extract_text(soup, 'Packaging'),
            'imdb_id': imdb_id
        }

        return jsonify(response_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
