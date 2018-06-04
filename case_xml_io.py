from pyquery import PyQuery

### stuff for loading and parsing case xml ###

namespaces = {
    'METS': 'http://www.loc.gov/METS/',
    'case': 'http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case:v1',
    'casebody': 'http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Case_Body:v1',
    'volume': 'http://nrs.harvard.edu/urn-3:HLS.Libr.US_Case_Law.Schema.Volume:v1',
    'xlink': 'http://www.w3.org/1999/xlink',
    'alto': 'http://www.loc.gov/standards/alto/ns-v3#',
}


def parse_file(path):
    return PyQuery(url=path, opener=open, encoding='UTF-8', parser='xml', namespaces=namespaces)


def get_case_text(case):
    if type(case) == str and case[-4:] == '.xml':
        case = parse_file(case)
    elif type(case) == str:
        return ''

    # strip labels from footnotes:
    for footnote in case('casebody|footnote'):
        label = footnote.attrib.get('label')
        if label and footnote[0].text.startswith(label):
            footnote[0].text = footnote[0].text[len(label):]

    text_elems = case('casebody|p')
    text_strings = list(map(lambda elem: elem.text(), text_elems.items()))
    text = "\n\n".join(text_strings)

    # strip soft hyphens from line endings
    text = text.replace(u'\xad', '')

    return text


def print_file_contents(filename):

    pq = parse_file(filename)

    file_text = get_case_text(pq)

    print(file_text)
