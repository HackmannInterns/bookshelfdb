import time
import requests
import re
import shelve

def save_to_cache(key, value):
    # print("Writing to Cache")
    with shelve.open('cache.db') as db:
        db[key] = value

def load_from_cache(key):
    with shelve.open('cache.db') as db:
        return db.get(key)

def api(id, identifier, use_cache):
    # Cache
    cached = load_from_cache(f"{identifier}:{id}")
    if use_cache and cached:
        # print("Hit cache")
        return cached
    # print("Miss cache")

    try:
        url = f"https://openlibrary.org/api/books?bibkeys={identifier}:{id}&format=json&jscmd=data"
        # print(url)
        response = requests.get(url)
        book_info = title = authors = publish_date = publisher = ""
        # print(response)
        if response.status_code == 200:
            data = response.json()
            save_to_cache(f"{identifier}:{id}", data)
        else:
            data = ""
    except:
        data = ""
    return (data)


def lookup_book_info(og_id, identifier, use_cache=True):
    if identifier == "isbn":
        og_id = og_id.replace("-", "")
    id = og_id.replace("-", "0")
    if len(id) == 9 and identifier == "isbn":
        id = "0" + og_id
    identifier = identifier.upper()

    data = api(id, identifier, use_cache)
    # print(data)
    title = authors = publish_date = publisher = "" 
    if len(data) > 0:
        # print("here")
        book_info = data[f"{identifier}:{id}"]
        title = book_info.get('title', 'Title not found')
        authors = ', '.join(author.get('name', 'Unknown Author')
                            for author in book_info.get('authors', []))
        publish_date = book_info.get(
            'publish_date', 'Publish date not found')
        match = re.search(r'\b\d{4}\b', publish_date)
        if match:
            publish_date = match.group()
        publisher = ', '.join(publisher.get('name', 'Unknown Author')
                              for publisher in book_info.get('publishers', []))
    return title, authors, publish_date, publisher


if __name__ == '__main__':
    data = lookup_book_info('9781778041303', 'isbn')
    for i in data:
        print(i)
    data = lookup_book_info('63-19392', 'lccn')  # has no ISBN
    for i in data:
        print(i)
