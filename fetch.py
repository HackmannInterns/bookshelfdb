import time
import requests
# title, author, publisher

def lookup_book_info(og_id, identifier):
    id = og_id.replace("-", "0")
    if len(id) == 9 and identifier == "isbn":
        id = "0" + isbn

    url = f"https://openlibrary.org/api/books?bibkeys={identifier.upper()}:{id}&format=json&jscmd=data"
    # print(url)
    response = requests.get(url)
    book_info = title = authors = publish_date = publisher = None
    # print(response)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        if len(data) > 0:
            # print("here")
            book_info = data[f"{identifier.upper()}:{id}"]
            title = book_info.get('title', 'Title not found')
            authors = ', '.join(author.get('name', 'Unknown Author')
                                for author in book_info.get('authors', []))
            publish_date = book_info.get(
                'publish_date', 'Publish date not found')
            publisher = ', '.join(publisher.get('name', 'Unknown Author')
                                  for publisher in book_info.get('publishers', []))
    return title, authors, publish_date, publisher


# if __name__ == '__main__':
    # data = lookup_book_info('9781778041303', 'isbn')
    # for i in data:
    #     print(i)
    # data = lookup_book_info('96154704', 'lccn')  # has ISBN
    # for i in data:
    #     print(i)
    # data = lookup_book_info('63-19392', 'lccn')  # has no ISBN
    # for i in data:
    #     print(i)
