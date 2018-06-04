def add_token_string_to_structure(structure, tokens, result_string):
    ''' Adds a token string to the structure described for the create_reporter_string_disambiguation_dict
    function.

     Args:
        structure: An object structured as described above for create_reporter_string_disambiguation_dict.
        tokens: A tokenized string (e.g., ['F.', '3d']).
        result_string: A proper reporter string (e.g., 'F.3d').

    Returns:
        Nothing. It makes the addition to 'structure' in place.
    '''
    structure_ptr = structure

    for i in range(0, len(tokens)):
        token = tokens[i]
        if token not in structure_ptr:
            structure_ptr[token] = {}
        structure_ptr = structure_ptr[token]

    structure_ptr[''] = result_string


def find_token_string_at_index(structure, words, start_index):
    i = start_index
    dict_ptr = structure

    while i < len(words):
        current_word = words[i]

        # Is the current word is one we expect to see in a valid reporter based on what we've seen so far?
        if current_word in dict_ptr:
            dict_ptr = dict_ptr[current_word]
            i = i + 1
        else:  # We ran into a word we didn't recognize
            break

    # If there's a '' entry where we broke, it means that we just saw a recognized reporter. If not, return None.
    result_string = dict_ptr.get('', None)
    end_index = i if (result_string is not None) else start_index + 1

    return end_index, result_string
