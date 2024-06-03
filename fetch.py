import requests


def lookup_book_info(isbn):
    if len(isbn) == 9:
        isbn = "0" + isbn

    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    print(url)
    response = requests.get(url)
    book_info = title = authors = publish_date = publisher = None
    # print(response)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        if f"ISBN:{isbn}" in data:
            book_info = data[f"ISBN:{isbn}"]
            title = book_info.get('title', 'Title not found')
            authors = ', '.join(author.get('name', 'Unknown Author')
                                for author in book_info.get('authors', []))
            publish_date = book_info.get(
                'publish_date', 'Publish date not found')
            publisher = ', '.join(publisher.get('name', 'Unknown Author')
                                  for publisher in book_info.get('publishers', []))
    return title, authors, publish_date, publisher
