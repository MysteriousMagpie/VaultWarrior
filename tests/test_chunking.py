from ai.core.index import chunk_markdown

def test_chunking_overlap():
    text = 'a' * 2500
    spans = chunk_markdown(text, 1200, 200)
    # expect 3 chunks: 0-1200, 1000-2200, 2000-2500
    assert spans[0] == (0, 1200)
    assert spans[1][0] == 1000
    assert spans[1][1] == 2200
    assert spans[2][0] == 2000
    assert spans[2][1] == 2500
