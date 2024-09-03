from blog.search import Index


def test_index(fake_document_list):
    document_list = fake_document_list
    index = Index()

    for doc in document_list:
        index.index_document(doc)

    assert index.document_frequency("photolithography") == 1
    assert index.document_frequency("photography") == 1
    assert index.document_frequency("a") == 0

    assert round(index.inverse_document_frequency("photolithography"), 4) == 0.6021
    assert round(index.inverse_document_frequency("light"), 4) == 0.1249

    rv = index.search("photolithography")
    assert len(rv) == 1
    assert rv[0].idx == 0

    rv = index.search("light")
    assert len(rv) == 3
    assert rv[0].idx == 0

    rv = index.search("light", rank=True)
    assert len(rv) == 3
    assert rv[0][0].idx == 2  # light sensor
    assert round(rv[0][1], 4) == 0.3748
