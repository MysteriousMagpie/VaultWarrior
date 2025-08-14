from ai.core.retrieve import format_citations

def test_citation_format():
    sample = [{
        'rank': 1,
        'file': 'notes/file.md',
        'heading': '# Heading',
        'start': 1234,
        'end': 5678,
    }]
    txt = format_citations(sample)
    assert 'notes/file.md' in txt
    assert '1' in txt
    assert '1,234' in txt or '1234' in txt
