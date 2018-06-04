from collections import namedtuple
from caseciteparser import constant_data

CitationState = namedtuple('CitationState', ['next_index', 'next_fn', 'citation_data', 'citation_is_ready'])

# Todo: create Enum for citation data


def parse_string(string):
    """ Returns parse_tokens(string.split())

    :param string: String to be parsed for citations.
    :return: A list of citation data
    """
    words = string.split()
    return parse_tokens(words)


def parse_tokens(words):
    """ Parses a list of word tokens and returns a list of dicts, where each item in the list corresponds to a legal
    case citation found in the list of word tokens. Each dict contains at least four keys:
        'reporter': the reporter abbreviation (e.g., 'F.3d');
        'volume': the volume of the reporter cited;
        'start_index': the index, in the list of words, of the first word of the citation; and
        'end_index': the index, in the list of words, of the last word of the citation.
    In addition, the dict contains one or more of the following keys:
        'case_first_page': the first page of the cited case;
        'pincite': the pin cite for the cited case;
        'cite_type': either "short_cite" or "full_cite", depending on the type of the citation;
        'stringcites': a list of dicts of string citation data, where each dict contains the volume, reporter, and first
            page of the stringcite;
        'year': the year the case was decided;
        'month': the month the case was decided;
        'day': the day the case was decided;
        'court_type': the type of the court (e.g., district, circuit, etc.); and
        'court_jurisdiction': the court's jurisdiction (e.g., a state or other geographical region).
    :param words: Word tokens to parse for citations.
    :return: A dict as described in the function description above.
    """
    return citation_fsm(words)


def get_number_or_range_word_starts_with(word):
    """ If the current word begins with a number or number range (i.e., a number followed by “-“, “–“, or “—“, followed
     by two digits), possibly with a comma or period after, then returns that number or number range.
     For example, get_word_ifstartswith_number_or_range("1234-56).") -> "1234-56"

    Args:
        word: the word.

    Returns:
        The number or number range. See function description.
    """
    for i in range(0, len(word)):
        if not word[i].isdigit():
            if word[i] == '-' or word[i] == '–' or word[i] == '—':
                if i + 2 < len(word) and word[i+1].isdigit() and word[i+2].isdigit():
                    return word[0:i+3]
                else:
                    return word[0:i]
            else:
                if i > 0:
                    return word[0:i]
                else:
                    return None

    return word


def word_is_number_followed_by_comma(word):
    return (len(word) > 1) and word[0:len(word)-1].isdigit() and word[len(word)-1] == ','


def citation_fsm(words):
    cite_list = []
    state = CitationState(next_index=1, next_fn=do_scan_for_reporter, citation_data={}, citation_is_ready=False)

    while state.next_index < len(words):
        # Call next function
        next_state = state.next_fn(words, state.next_index, state.citation_data)

        # If a citation is ready, add it to the list
        if next_state.citation_is_ready:
            cite_list.append(next_state.citation_data)
            state = CitationState(next_index=next_state.next_index, next_fn=next_state.next_fn,
                                  citation_data={}, citation_is_ready=False)
        else:  # Transition to the next state
            state = next_state

    return cite_list


def failure_citation_state(index):
    return CitationState(next_index=index, next_fn=do_scan_for_reporter, citation_data={}, citation_is_ready=False)


def do_scan_for_reporter(words, index, citation_data):
    (end_index, reporter_str) = constant_data.find_reporter_at_index(words, index)

    if reporter_str is not None and words[index-1].isdigit():  # Recognized a reporter preceded by a volume number
        citation_data['reporter'] = reporter_str
        citation_data['volume'] = words[index-1]
        citation_data['start_index'] = index-1
        return CitationState(next_index=end_index, next_fn=do_reporter_found,
                             citation_data=citation_data, citation_is_ready=False)
    else:
        return failure_citation_state(end_index)


def do_reporter_found(words, index, citation_data):
    current_word = words[index]

    if current_word == "at":
        return CitationState(next_index=index + 1, next_fn=do_parse_short_cite_pincite,
                             citation_data=citation_data, citation_is_ready=False)
    elif current_word.isdigit():  # The current word is a number WITHOUT comma at the end.
        citation_data['case_first_page'] = current_word
        return CitationState(next_index=index + 1, next_fn=do_parse_date_parenthetical,
                             citation_data=citation_data, citation_is_ready=False)
    elif word_is_number_followed_by_comma(current_word): # The current word is a number WITH comma at the end.
        citation_data['case_first_page'] = get_number_or_range_word_starts_with(current_word)
        return CitationState(next_index=index + 1, next_fn=do_parse_stringcite_or_pincite,
                             citation_data=citation_data, citation_is_ready=False)
    else:  # Failure
        return failure_citation_state(citation_data['start_index']+2)


def do_parse_short_cite_pincite(words, index, citation_data):
    current_word = words[index]

    pincite_if_valid = get_number_or_range_word_starts_with(current_word)

    if pincite_if_valid is not None:
        citation_data['pincite'] = pincite_if_valid
        citation_data['end_index'] = index
        citation_data['cite_string'] = " ".join(words[citation_data['start_index']:index+1])
        citation_data['cite_type'] = 'short_cite'
        return CitationState(next_index=index + 1, next_fn=do_scan_for_reporter,
                             citation_data=citation_data, citation_is_ready=True)
    else:  # Failure
        return failure_citation_state(citation_data['start_index']+2)


def add_stringcite_to_citation_data(volume, reporter, case_first_page, citation_data):
    stringcite = {}
    stringcite['volume'] = volume
    stringcite['reporter'] = reporter
    stringcite['case_first_page'] = case_first_page

    if 'stringcites' not in citation_data:
        citation_data['stringcites'] = []

    citation_data['stringcites'].append(stringcite)


def do_parse_stringcite_or_pincite(words, index, citation_data):
    current_word = words[index]
    if current_word.isdigit():  # The current word is a number
        (reporter_end_index, reporter_str) = constant_data.find_reporter_at_index(words, index + 1)
        if (reporter_str is not None) and (reporter_end_index < len(words)):  # The next word is the start of a reporter
            possible_stringcite_firstpage = words[reporter_end_index]

            # The word after the reporter is a number WITHOUT a comma
            if possible_stringcite_firstpage.isdigit():
                add_stringcite_to_citation_data(current_word, reporter_str, possible_stringcite_firstpage, citation_data)

                return CitationState(next_index=reporter_end_index + 1, next_fn=do_parse_date_parenthetical,
                                     citation_data=citation_data, citation_is_ready=False)

            # The word after the reporter is a number WITH a comma
            elif word_is_number_followed_by_comma(possible_stringcite_firstpage):
                add_stringcite_to_citation_data(current_word, reporter_str,
                                                possible_stringcite_firstpage[0:len(possible_stringcite_firstpage)-1],
                                                citation_data)

                return CitationState(next_index=reporter_end_index + 1, next_fn=do_parse_stringcite,
                                     citation_data=citation_data, citation_is_ready=False)

    pincite_if_valid = get_number_or_range_word_starts_with(current_word)

    if pincite_if_valid is not None:
        if current_word == pincite_if_valid:  # If the current word is a pincite WITHOUT a comma
            citation_data['pincite'] = pincite_if_valid
            return CitationState(next_index=index + 1, next_fn=do_parse_date_parenthetical,
                                 citation_data=citation_data, citation_is_ready=False)

        elif current_word == (pincite_if_valid + ','): # If the current word is a pincite WITH a comma
            citation_data['pincite'] = pincite_if_valid
            return CitationState(next_index=index + 1, next_fn=do_parse_stringcite,
                                 citation_data=citation_data, citation_is_ready=False)

    return failure_citation_state(citation_data['start_index']+2)


def do_parse_stringcite(words, index, citation_data):
    current_word = words[index]

    if current_word.isdigit():  # The current word is a number
        (reporter_end_index, reporter_str) = constant_data.find_reporter_at_index(words, index + 1)
        if (reporter_str is not None) and (reporter_end_index < len(words)):  # The next word is the start of a reporter
            possible_stringcite_firstpage = words[reporter_end_index]

            # The word after the reporter is a number WITHOUT a comma
            if possible_stringcite_firstpage.isdigit():
                add_stringcite_to_citation_data(current_word, reporter_str, possible_stringcite_firstpage, citation_data)

                return CitationState(next_index=reporter_end_index + 1, next_fn=do_parse_date_parenthetical,
                                     citation_data=citation_data, citation_is_ready=False)

            # The word after the reporter is a number WITH a comma
            elif word_is_number_followed_by_comma(possible_stringcite_firstpage):
                add_stringcite_to_citation_data(current_word, reporter_str,
                                                possible_stringcite_firstpage[0:len(possible_stringcite_firstpage)-1],
                                                citation_data)

                return CitationState(next_index=reporter_end_index + 1, next_fn=do_parse_stringcite,
                                     citation_data=citation_data, citation_is_ready=False)

    return failure_citation_state(citation_data['start_index']+2)


def do_parse_date_parenthetical(words, index, citation_data):
    current_word = words[index]

    # If the current word doesn't start with a '(', fail
    if (len(current_word) == 0) or (current_word[0] != '('):
        return CitationState(next_index=index + 1, next_fn=do_scan_for_reporter,
                             citation_data={}, citation_is_ready=False)

    paren_string = words[index]

    while index < len(words):
        if paren_string.find(')') != -1:
            paren_string = paren_string[1:paren_string.find(')')]
            paren_data = parenthetical_fsm(paren_string)
            citation_data.update(paren_data)
            citation_data['end_index'] = index
            citation_data['cite_string'] = " ".join(words[citation_data['start_index']:index + 1])
            citation_data['cite_type'] = 'full_cite'
            return CitationState(next_index=index + 1, next_fn=do_scan_for_reporter,
                                 citation_data=citation_data, citation_is_ready=True)
        elif len(paren_string) > 50:  # Couldn't find a close paren in time
            return failure_citation_state(citation_data['start_index']+2)
        else:
            index = index + 1
            paren_string = paren_string + ' ' + words[index]

    # We ran out of words and still didn't find our paren!
    return failure_citation_state(citation_data['start_index']+2)


def parenthetical_fsm(paren_string):
    paren_string = paren_string.strip()
    paren_tokens = paren_string.split()

    paren_data = {'date_paren_string': paren_string}

    # Parse year (it's always going to be there
    possible_year = paren_tokens.pop()
    if (len(possible_year) != 4) or (not possible_year.isdigit()):
        return paren_data
    paren_data['year'] = possible_year

    state = CitationState(next_index=0, next_fn=do_parse_court, citation_data=paren_data, citation_is_ready=False)

    while state.next_index < len(paren_tokens) and state.next_fn is not None:
        # Call next function
        next_state = state.next_fn(paren_tokens, state.next_index, state.citation_data)

        # Transition to the next state
        state = next_state

    return paren_data


def do_parse_court(paren_tokens, index, paren_data):
    # Parse court
    (court_end_index, court_string) = constant_data.find_court_at_index(paren_tokens, index)

    if court_string is not None:
        paren_data['court_type'] = court_string
        index = court_end_index

        (geo_end_index, geo_string) = constant_data.find_geo_at_index(paren_tokens, index)

        if geo_string is not None:
            paren_data['court_jursidiction'] = geo_string
            index = geo_end_index

    else:
        (geo_end_index, geo_string) = constant_data.find_geo_at_index(paren_tokens, index)

        if geo_string is not None:
            paren_data['court_jursidiction'] = geo_string
            index = geo_end_index

            (court_end_index, court_string) = constant_data.find_court_at_index(paren_tokens, index)
            if court_string is not None:
                paren_data['court_type'] = court_string
                index = court_end_index

    return CitationState(next_index=index, next_fn=do_parse_month_day,
                         citation_data=paren_data, citation_is_ready=False)


def do_parse_month_day(paren_tokens, index, paren_data):
    # Parse mon/day
    # Is the current word a valid month abbreviation?
    (month_end_index, month_string) = constant_data.find_month_at_index(paren_tokens, index)

    if month_string is not None:
        index = month_end_index

        # Is the next word a number followed by a comma?
        if index < len(paren_tokens) and word_is_number_followed_by_comma(paren_tokens[index]):
            # If so, save the mon/day
            paren_data['month'] = month_string
            paren_data['day'] = paren_tokens[index][0:len(paren_tokens[index])-1]

    return CitationState(next_index=index, next_fn=None,
                         citation_data=paren_data, citation_is_ready=False)

