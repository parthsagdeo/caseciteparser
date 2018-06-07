About
=====================

A parser for legal case citations.

Installation
=====================
You can install ``caseciteparser`` by running:

::

    pip install caseciteparser
	
Usage
=====================

There are two user-facing functions in ``caseciteparser``: ``parse_tokens(words)`` and ``parse_string(string)``.

``parse_tokens(words)`` parses a list of whitespace-delimited tokens and returns a list of dicts, where each item in the list corresponds to a legal case citation found in the list of word tokens.
 
``parse_string(string)`` parses a string by calling ``parse_tokens(string.split())``.
 

Examples
=====================

Importing ``caseciteparser`` (and ``pprint`` for readability): ::

	>>> from caseciteparser import parse_string
	>>> from pprint import pprint

Parsing a federal district court case with a pincite: ::

	>>> pprint(parse_string("Charlesworth v. Mack, 727 F. Supp. 1407, 1412 (D. Mass. 1990)."))
	[{'case_first_page': '1407',
	  'cite_string': '727 F. Supp. 1407, 1412 (D. Mass. 1990).',
	  'cite_type': 'full_cite',
	  'court_jursidiction': 'Mass.',
	  'court_type': 'D.',
	  'date_paren_string': 'D. Mass. 1990',
	  'end_index': 10,
	  'pincite': '1412',
	  'reporter': 'F. Supp.',
	  'start_index': 3,
	  'volume': '727',
	  'year': '1990'}]

Parsing a string cite: ::

	>>> pprint(parse_string("Mydlach v. DaimlerChrysler Corp., 226 Ill. 2d 307, 311, 875 N.E.2d 1047 (2007)."))
	[{'case_first_page': '307',
	  'cite_string': '226 Ill. 2d 307, 311, 875 N.E.2d 1047 (2007).',
	  'cite_type': 'full_cite',
	  'date_paren_string': '2007',
	  'end_index': 12,
	  'pincite': '311',
	  'reporter': 'Ill. 2d',
	  'start_index': 4,
	  'stringcites': [{'case_first_page': '1047',
					   'reporter': 'N.E.2d',
					   'volume': '875'}],
	  'volume': '226',
	  'year': '2007'}]

Parsing a short form citation.::

	>>> pprint(parse_string("Youngstown, 343 U.S. at 585."))
	[{'cite_string': '343 U.S. at 585.',
	  'cite_type': 'short_cite',
	  'end_index': 4,
	  'pincite': '585',
	  'reporter': 'U.S.',
	  'start_index': 1,
	  'volume': '343'}]

Parsing a sentence with multiple citations: ::

	>>> pprint(parse_string("Although Illinois law recognizes limitation periods as valid contractual \
			provisions in an insurance contract, see, e.g., Affiliated FM Insurance Co. v. Board of Education, \
			23 F.3d 1261, 1264 (7th Cir. 1994) (and cases cited therein), section 143.1 of the Code is an \
			important statutory restriction on such limitation provisions, Hines v. Allstate Insurance Co., \
			298 Ill. App. 3d 585, 588, 698 N.E.2d 1120 (1998)."))
	[{'case_first_page': '1261',
	  'cite_string': '23 F.3d 1261, 1264 (7th Cir. 1994)',
	  'cite_type': 'full_cite',
	  'court_jursidiction': '7th',
	  'court_type': 'Cir.',
	  'date_paren_string': '7th Cir. 1994',
	  'end_index': 30,
	  'pincite': '1264',
	  'reporter': 'F.3d',
	  'start_index': 24,
	  'volume': '23',
	  'year': '1994'},
	 {'case_first_page': '585',
	  'cite_string': '298 Ill. App. 3d 585, 588, 698 N.E.2d 1120 (1998).',
	  'cite_type': 'full_cite',
	  'date_paren_string': '1998',
	  'end_index': 63,
	  'pincite': '588',
	  'reporter': 'Ill. App. 3d',
	  'start_index': 54,
	  'stringcites': [{'case_first_page': '1120',
					   'reporter': 'N.E.2d',
					   'volume': '698'}],
	  'volume': '298',
	  'year': '1998'}]
	  
License/Attribution
=====================

This project is licensed under the GNU Affero General Public License, with the additional condition that you provide attribution to this project if you use it for academic research that results in the publication of a paper. See the ``LICENSE`` file for the actual terms of the license.
	  
Contact
=====================
Feel free to send me a message if you have any questions, or comments, or even to let me know how you're using ``caseciteparser``! I'm really interested to see what people are doing with automated analysis of caselaw!