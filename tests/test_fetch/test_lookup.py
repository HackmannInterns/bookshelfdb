import responses
import json
from fetch import lookup_book_info


def test_lookup_book_data():
    book_id = '9781778041303'
    id_type = 'isbn'
    url = f"https://openlibrary.org/api/books?bibkeys={id_type}:{book_id}&format=json&jscmd=data"
    mock_response = """{"ISBN:9781778041303": {"url": "https://openlibrary.org/books/OL49098336M/Plague_of_Models", "key": "/books/OL49098336M", "title": "Plague of Models", "subtitle": "How Computer Modeling Corrupted Environmental, Health, and Safety Regulations", "authors": [{"url": "https://openlibrary.org/authors/OL12308828A/Kenneth_P._Green", "name": "Kenneth P. Green"}, {"url": "https://openlibrary.org/authors/OL765044A/Benjamin_Zycher", "name": "Benjamin Zycher"}, {"url": "https://openlibrary.org/authors/OL49490A/Steven_F._Hayward", "name": "Steven F. Hayward"}], "pagination": "242", "weight": "0.327", "identifiers": {"isbn_13": ["9781778041303"], "openlibrary": ["OL49098336M"]}, "publishers": [{"name": "Matos, Melissa"}], "publish_date": "2023"}}"""
    mock_response = json.loads(mock_response)
    responses.add(responses.GET, url, json=mock_response, status=200)

    # test api without cache
    title, authors, publish_date, publisher, subjects = lookup_book_info(
        book_id, id_type, False)

    assert title == "Plague of Models"
    assert authors == "Kenneth P. Green, Benjamin Zycher, Steven F. Hayward"
    assert publish_date == "2023"
    assert publisher == "Matos, Melissa"
    assert subjects == ""
