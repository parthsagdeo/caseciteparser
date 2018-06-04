from pprint import pprint
import caseciteparser
import case_xml_io


def test(do_interactive_mode):
    if do_interactive_mode:
        do_interactive_tests()


def do_interactive_tests():
    print("~~~~~INTERACTIVE MODE~~~~~")

    do_interactive_case_xml_test()

    print()

    do_interactive_user_input_test()


def do_interactive_case_xml_test():
    case_xml_filename = input("Enter a case XML file to extract citations from (press Enter to skip): ")

    if case_xml_filename == '':
        return

    print("Extracting case text from " + case_xml_filename)
    case_text = case_xml_io.get_case_text(case_xml_filename)

    print("Printing citations extracted from the above case text:")
    case_text_tokens = case_text.split()
    cite_list = caseciteparser.parse_tokens(case_text_tokens)
    pprint(cite_list)

    print("Printing recognized citations (and 7 tokens before/after).")
    i = 1
    for cite in cite_list:
        print(str(i) + ") " + " ".join(
            case_text_tokens[cite['start_index'] - 7:cite['start_index']]) +
              " <<<" + " ".join(case_text_tokens[cite['start_index']:cite['end_index'] + 1]) + ">>> " +
              " ".join(case_text_tokens[cite['end_index'] + 1:cite['end_index'] + 8]) + " ")
        i += 1


def do_interactive_user_input_test():
    print("Instructions: type in a citation and I will try to parse it!\nRight now I only support case citations (both "
          "short cites and full cites (with or without string cites) are okay).\nPress Enter to skip.")

    user_string = input("Enter citation: ")

    while user_string != "":
        user_cite_list = caseciteparser.parse(user_string)
        if len(user_cite_list) == 0:
            print("Could not parse citation!")
        else:
            pprint(user_cite_list)

        user_string = input("Enter citation: ")


test(True)