from caseciteparser import token_dict
from reporters_db import REPORTERS

COURT_ABBREVIATIONS = ['Admin. Ct.', 'Adm.', 'Alder. Ct.', 'App. Ct.', 'App. Ct.', 'App. Dep’t', 'App. Div.', 'ASBCA',
                       'B.A.P.', 'Bankr.', 'B.C.A.', 'B.I.A.', 'B.P.A.I.', 'B.T.A.', 'Bor. Ct.', 'C.D.', 'Ch.',
                       'Child. Ct.', 'C.C.', 'Cir. Ct.', 'Cir.', 'Cir. Ct. App.', 'City Ct.', 'Civ. App.',
                       'Civ. Ct. Rec.', 'Civ. Dist. Ct.', 'Cl. Ct.', 'Comm. Ct.', 'Comm’n', 'C.P.', 'Commw. Ct.',
                       'Concil. Ct.', 'Cty. J. Ct.', 'Ct.', 'C.A.', 'Cir.', 'Ct. App.', 'C.A.A.F.', 'Civ. App.',
                       'Ct. Cl.', 'Ct. Com. Pl.', 'Crim. App.', 'C.C.P.A.', 'Ct. Cust. App.', 'Ct. Err.',
                       'Ct. Err. & App.', 'Fed. Cl.', 'Ct. Gen. Sess.', 'Ct. Spec. Sess.', 'Ct. Int’l Trade', 'C.M.A.',
                       'C.M.R.', 'Ct. Spec. App.', 'Ct. Vet. App.', 'Crim. App.', 'Crim. Dist. Ct.', 'Cust. Ct.', 'D.',
                       'Dist. Ct.', 'Dist. Ct. App.', 'Div.', 'Dom. Rel. Ct.', 'E.D.', 'Emer. Ct. App.', 'Eq.',
                       'Fam. Ct.', 'High Ct.', 'Jud. Dist.', 'Jud. Div.', 'J.P.M.L.', 'J.P. Ct.', 'Juv. Ct.',
                       'Land Ct.', 'Law Ct.', 'Law Div.', 'Magis. Div.', 'Magis. Ct.', 'M.D.', 'Mun. Ct.', 'N.D.',
                       'Orphans’ Ct.', 'Parish Ct.', 'Police J. Ct.', 'Prerog. Ct.', 'Prob. Ct.', 'P.U.C.',
                       'Real Est. Comm’n', 'Rec’s Ct.', 'S.D.', 'Reg’l Rail Reorg. Ct.', 'Super. Ct.', 'U.S.',
                       'Sup. Ct.', 'App. Div.', 'App. Term', 'Sup. Ct. Err.', 'Sup. Jud. Ct.', 'Sur. Ct.',
                       'Tax App. Ct.', 'T.C.', 'Teen Ct.', 'Temp. Emer. Ct. App.', 'Terr.', 'T.T.A.B.', 'Traffic Ct.',
                       'Tribal Ct.', 'Trib.', 'Water Ct.', 'W.D.', 'Workmen’s Comp. Div.', 'Youth Ct.']

GEOGRAPHIC_ABBREVIATIONS = ['Ala.', 'Alaska', 'Ariz.', 'Ark.', 'Cal.', 'Colo.', 'Conn.', 'Del.', 'Fla.', 'Ga.', 'Haw.',
                            'Idaho', 'Ill.', 'Ind.', 'Iowa', 'Kan.', 'Ky.', 'La.', 'Me.', 'Md.', 'Mass.', 'Mich.',
                            'Minn.', 'Miss.', 'Mo.', 'Mont.', 'Neb.', 'Nev.', 'N.H.', 'N.J.', 'N.M.', 'N.Y.', 'N.C.',
                            'N.D.', 'Ohio', 'Okla.', 'Or.', 'Pa.', 'R.I.', 'S.C.', 'S.D.', 'Tenn.', 'Tex.', 'Utah',
                            'Vt.', 'Va.', 'Wash.', 'W. Va.', 'Wis.', 'Wyo.', 'Balt.', 'Bos.', 'Chi.', 'Dall.', 'D.C.',
                            'Hous.', 'L.A.', 'N.Y.C.', 'Phila.', 'Phx.', 'S.F.', 'Am. Sam.', 'Guam', 'N. Mar. I.',
                            'P.R.', 'V.I.', '1st', '2d', '3d', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th',
                            'Fed.']

MONTH_ABBREVIATIONS = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']


def create_reporter_token_disambiguation_dict(reporters):
    """ Creates a structure of the form {<reporter token_1>: {... -> {<reporter token_N>: {'' -> <proper reporter>}}}}.
    For example, 'F. 3d' would get mapped to 'F.' -> '3d.' -> '' -> 'F.3d'. This is useful so we can efficiently check
    whether a given string is a recognized reporter abbreviation, and, if so, determine the corresponding proper Bluebook
    reporter abbreviation.

    Args:
        reporters: An object structured like the 'REPORTERS' object in Free Law Project's reporters_db package.

    Returns:
        A dict of the form described above.

    """

    reporter_token_disambiguation_dict =  {}

    for reporter_base, reporter_data in reporters.items():
        reporter_editions = reporter_data[0]['editions']
        reporter_variations = reporter_data[0]['variations']

        # The keys in the 'editions' dict are the proper reporter names, so they just map to themselves
        for reporter_edition in reporter_editions:
            token_dict.add_token_string_to_structure(reporter_token_disambiguation_dict, reporter_edition.split(),
                                          reporter_edition)

        # The 'variations' dict basically already has the mappings we want
        for reporter_variation, reporter_variation_proper in reporter_variations.items():
            token_dict.add_token_string_to_structure(reporter_token_disambiguation_dict, reporter_variation.split(),
                                          reporter_variation_proper)

    return reporter_token_disambiguation_dict


def find_reporter_at_index(words, start_index):
    """ Determine the full reporter starting at the specified index
    Args:
        words: the array of words to operate on.
        start_index: the first index to look at. This function assumes that the reporter starts on start_index.

    Returns:
         A tuple of the form (end_index, proper_reporter).
            end_index is the index after the last word of the reporter, or start_index + 1 if no reporter is recognized.
            proper_reporter is either None or the proper Bluebook form of the reporter found.

         For example:
                  disambiguate_reporter(['blabla', 'F.', '3d.', 'asdasd'], 0) -> (0, None)
                  disambiguate_reporter(['blabla', 'F.', '3d.', 'asdasd'], 1) -> (3, 'F.3d')
    """

    return token_dict.find_token_string_at_index(REPORTER_TOKEN_DISAMBIGUATION_DICT, words, start_index)


def create_token_dict_from_string_list(string_list):
    structure = {}
    for string_elem in string_list:
        token_dict.add_token_string_to_structure(structure, string_elem.split(), string_elem)
    return structure


def find_court_at_index(words, start_index):
    return token_dict.find_token_string_at_index(COURT_TOKEN_DICT, words, start_index)


def find_geo_at_index(words, start_index):
    return token_dict.find_token_string_at_index(GEO_TOKEN_DICT, words, start_index)


def find_month_at_index(words, start_index):
    return token_dict.find_token_string_at_index(MONTH_TOKEN_DICT, words, start_index)


REPORTER_TOKEN_DISAMBIGUATION_DICT = create_reporter_token_disambiguation_dict(REPORTERS)
COURT_TOKEN_DICT = create_token_dict_from_string_list(COURT_ABBREVIATIONS)
GEO_TOKEN_DICT = create_token_dict_from_string_list(GEOGRAPHIC_ABBREVIATIONS)
MONTH_TOKEN_DICT = create_token_dict_from_string_list(MONTH_ABBREVIATIONS)