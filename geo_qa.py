import rdflib
import ontology
import questions_handler

CREATE = 'create'
QUESTION = 'question'

g = rdflib.Graph()


def validate_args(args):
    if len(args) == 2 and args[1] == CREATE:
        return True
    elif len(args) == 3 and args[1] == QUESTION:
        return True
    else:
        print('Usage: {0} create or {0} question \"<question>\"'.format(args[0]))
        return False


def main(args):
    if validate_args(args) is False:
        return
    if args[1] == CREATE:
        ontology.build_ontology()
    else:
        questions_handler.handler(args[2])


if __name__ == '__main__':
    import sys
    main(sys.argv)
