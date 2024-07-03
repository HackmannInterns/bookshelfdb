import requests
import re
import shelve
from requests.exceptions import ConnectionError

CACHE_DB_LOCATION = 'data/cache.db'


def save_to_cache(key, value):
    # print("Writing to Cache")
    with shelve.open(CACHE_DB_LOCATION) as db:
        db[key] = value


def load_from_cache(key):
    with shelve.open(CACHE_DB_LOCATION) as db:
        return db.get(key)


def api(key, url, use_cache):
    # print(url)

    # Cache
    cached = load_from_cache(key)
    if use_cache and cached:
        # print("Hit cache")
        return cached
    # print("Miss cache")

    try:
        # print(url)
        response = requests.get(url)
        # print(response)
        if response.status_code == 200:
            data = response.json()
            save_to_cache(key, data)
        else:
            data = ""
    except ConnectionError as e:
        print(e)
        data = ""
    return data


def correct_id(og_id, identifier):
    if identifier == "isbn":
        og_id = og_id.replace("-", "")
    id = og_id.replace("-", "0")
    if len(id) == 9 and identifier == "isbn":
        id = "0" + og_id
    identifier = identifier.upper()

    return id, identifier


def parse_book_data(book_info):
    title = book_info.get('title', '')
    authors = ', '.join(author.get('name', '')
                        for author in book_info.get('authors', []))
    publish_date = book_info.get(
        'publish_date', '')
    match = re.search(r'\b\d{4}\b', publish_date)
    if match:
        publish_date = match.group()
    publisher = ', '.join(publisher.get('name', '')
                          for publisher in book_info.get('publishers', []))

    all_subjects = book_info.get('subjects', [])
    all_subjects += book_info.get('subject_places', [])
    all_subjects += book_info.get('subject_people', [])
    all_subjects += book_info.get('subject_times', [])
    # print(all_subjects)
    subjects = list(subject.get('name', '')
                    for subject in all_subjects)
    subjects = ', '.join(subjects)
    return title, authors, publish_date, publisher, subjects


def parse_data(data, identifier, book_id):
    title = authors = publish_date = publisher = subjects = ""
    if len(data) > 0:
        # print("here")
        book_info = data[f"{identifier}:{book_id}"]
        title, authors, publish_date, publisher, subjects = parse_book_data(
            book_info)
    return title, authors, publish_date, publisher, subjects


def lookup_book_info(og_id, identifier, use_cache=True):
    book_id, identifier = correct_id(og_id, identifier)
    data = api(f"{identifier}:{book_id}",
               f"https://openlibrary.org/api/books?bibkeys={identifier}:{book_id}&format=json&jscmd=data", use_cache)
    # print(data)
    # print(type(data))
    title, authors, publish_date, publisher, subjects = parse_data(
        data, identifier, book_id)
    return title, authors, publish_date, publisher, subjects


def search_by_author_title(author, title, use_cache=True):
    if title == "":
        title = '""'
    if author == "":
        author = '""'
    url = f"https://openlibrary.org/search.json?title={title}&author={author}&fields=edition_key"
    data = api(f"{author}:{title}", url, use_cache)

    olids = []
    results = data.get('docs', [])
    for result in results:
        olids.append(result.get('edition_key')[0])

    master_list = []
    for i in olids[:50]:
        b_id = i.split('/')[-1]
        indiv_data = api(
            f'OLID:{b_id}', f"https://openlibrary.org/api/books?bibkeys=OLID:{b_id}&format=json&jscmd=data", use_cache)
        title, authors, publish_date, publisher, subjects = parse_data(
            indiv_data, "OLID", b_id)
        book = {}
        book['olid'] = b_id
        book['title'] = title
        book['authors'] = authors
        book['publish_date'] = publish_date
        book['publisher'] = publisher
        book['subjects'] = subjects
        master_list.append(book)
    return (master_list)


# if __name__ == '__main__':
#     data = lookup_book_info('9781778041303', 'isbn', False)
#     for i in data:
#         print(i)
#     data = lookup_book_info('63-19392', 'lccn')  # has no ISBN
#     for i in data:
#         print(i)
#     search_by_author_title(author="",
#                            title="Alice in Wonderland")
