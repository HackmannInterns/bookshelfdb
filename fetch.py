import time
import requests
# title, author, publisher

def find_title(html_string):
    try:
        start_index = html_string.index('page-heading-small')
        start_title = html_string.index('</small>', start_index)+8
        end_title = html_string.index('</h1>', start_index)
        print('title:')
        print(html_string[start_title:end_title])
        return html_string[start_title:end_title]
    except:
        print("no title found")
        return None

def find_author(html_string):
    try:
        start_index = html_string.index('Personal name')
        start_author = html_string.index('<span dir="ltr">', start_index) + 16
        end_author = html_string.index('</span></a>', start_index)
        print('author:')
        print(html_string[start_author:end_author])
        return html_string[start_author:end_author]
    except:
        print("no author found")
        return None


def find_isbn(html_string):
    try:
        start_isbn = html_string.index('isbn') + 5
        end_isbn = html_string.index('&', start_isbn)
        print('isbn:')
        print(html_string[start_isbn:end_isbn])
        return html_string[start_isbn:end_isbn]
    except:
        print("no isbn found")
        return None

def lookup_book_lccn(lccn):
    html = "https://lccn.loc.gov/"+lccn
    html_string = ""
    title = None
    author = None
    publisher = None
    content = 0
    html_string = requests.request("GET", html).text
    while '<title>LC Catalog - No Connections Available</title>' in html_string:
        html_string = requests.request("GET", html).text
        time.sleep(6.5)
    title = find_title(html_string)
    author = find_author(html_string)
    isbn = find_isbn(html_string)
    return title, author, None, None, isbn





# Order of returns is title, author, publish date, publisher, isbn
def lookup_book_info(idenfier, type):
    if type == 'lccn':
        return lookup_book_lccn(idenfier)
    elif type == 'isbn':
        return lookup_book_isbn(idenfier)
    else:
        print('Big ol error')

#
def lookup_book_isbn(isbn):
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


lookup_book_info(96154704, 'isbn')
lookup_book_info(9781778041310, 'isbn')