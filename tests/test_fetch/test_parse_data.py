import json
from fetch import parse_data

def test_fetch_book_parse_data_lccn():
    mock_data = """{"LCCN:63019392": {"url": "https://openlibrary.org/books/OL5886814M/The_Chinese-kosher_cookbook", "key": "/books/OL5886814M", "title": "The Chinese-kosher cookbook", "authors": [{"url": "https://openlibrary.org/authors/OL709676A/Ruth_Grossman", "name": "Ruth Grossman"}], "number_of_pages": 83, "pagination": "xii, 83 p.", "by_statement": "by Ruth and Bob Grossman.", "identifiers": {"librarything": ["2855003"], "lccn": ["63019392"], "oclc": ["4993757"], "openlibrary": ["OL5886814M"]}, "classifications": {"lc_classifications": ["TX724 .G73"], "dewey_decimal_class": ["641.567"]}, "publishers": [{"name": "P.S. Eriksson"}], "publish_places": [{"name": "New York"}], "publish_date": "1963", "subjects": [{"name": "Chinese Cookery", "url": "https://openlibrary.org/subjects/chinese_cookery"}, {"name": "Jewish Cookery", "url": "https://openlibrary.org/subjects/jewish_cookery"}, {"name": "Jewish cooking", "url": "https://openlibrary.org/subjects/jewish_cooking"}, {"name": "Chinese Cooking", "url": "https://openlibrary.org/subjects/chinese_cooking"}], "ebooks": [{"preview_url": "https://archive.org/details/chinesekoshercoo00gros", "availability": "borrow", "formats": {}, "borrow_url": "https://openlibrary.org/books/OL5886814M/The_Chinese-kosher_cookbook/borrow", "checkedout": false}], "cover": {"small": "https://covers.openlibrary.org/b/id/6470482-S.jpg", "medium": "https://covers.openlibrary.org/b/id/6470482-M.jpg", "large": "https://covers.openlibrary.org/b/id/6470482-L.jpg"}}}"""
    mock_data = json.loads(mock_data)
    book_id = "63019392"
    id_type = "LCCN"
    title, authors, publish_date, publisher, subjects = parse_data(mock_data, id_type, book_id)
    assert title == "The Chinese-kosher cookbook"
    assert authors == "Ruth Grossman"
    assert publish_date == "1963"
    assert publisher == "P.S. Eriksson"
    assert subjects == "Chinese Cookery, Jewish Cookery, Jewish cooking, Chinese Cooking"

def test_fetch_book_parse_data_isbn():
    mock_data = """{"ISBN:9781778041303": {"url": "https://openlibrary.org/books/OL49098336M/Plague_of_Models", "key": "/books/OL49098336M", "title": "Plague of Models", "subtitle": "How Computer Modeling Corrupted Environmental, Health, and Safety Regulations", "authors": [{"url": "https://openlibrary.org/authors/OL12308828A/Kenneth_P._Green", "name": "Kenneth P. Green"}, {"url": "https://openlibrary.org/authors/OL765044A/Benjamin_Zycher", "name": "Benjamin Zycher"}, {"url": "https://openlibrary.org/authors/OL49490A/Steven_F._Hayward", "name": "Steven F. Hayward"}], "pagination": "242", "weight": "0.327", "identifiers": {"isbn_13": ["9781778041303"], "openlibrary": ["OL49098336M"]}, "publishers": [{"name": "Matos, Melissa"}], "publish_date": "2023"}}"""
    mock_data = json.loads(mock_data)
    book_id = "9781778041303"
    id_type = "ISBN"
    title, authors, publish_date, publisher, subjects = parse_data(mock_data, id_type, book_id)
    assert title == "Plague of Models"
    assert authors == "Kenneth P. Green, Benjamin Zycher, Steven F. Hayward"
    assert publish_date == "2023"
    assert publisher == "Matos, Melissa"
    assert subjects == ""

def test_fetch_book_parse_data_empty_data():
    mock_data = {}
    book_id = "9781778041303"
    id_type = "ISBN"
    title, authors, publish_date, publisher, subjects = parse_data(mock_data, id_type, book_id)
    assert title == ""
    assert authors == ""
    assert publish_date == ""
    assert publisher == ""
    assert subjects == ""
