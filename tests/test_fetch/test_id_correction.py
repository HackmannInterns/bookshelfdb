from fetch import correct_id


def test_correct_id_isbn_dashes():
    book_id = "978-0-9940969-0-6"
    id_type = "isbn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "9780994096906"
    assert new_type == "ISBN"


def test_correct_id_isbn_no_dashes():
    book_id = "9780994096906"
    id_type = "isbn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "9780994096906"
    assert new_type == "ISBN"


def test_correct_id_sbn_dashes():
    book_id = "671-75625-7"
    id_type = "isbn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "0671756257"
    assert new_type == "ISBN"


def test_correct_id_sbn_no_dashes():
    book_id = "671756257"
    id_type = "isbn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "0671756257"
    assert new_type == "ISBN"


def test_correct_id_lccn_dashes():
    book_id = "63-19392"
    id_type = "lccn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "63019392"
    assert new_type == "LCCN"


def test_correct_id_lccn_no_dashes():
    book_id = "63019392"
    id_type = "lccn"
    new_id, new_type = correct_id(book_id, id_type)

    assert new_id == "63019392"
    assert new_type == "LCCN"
