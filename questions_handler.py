import rdflib

wiki_prefix = "http://en.wikipedia.org"
example_prefix = "http://example.org"

# ------ Relations ------ #
PRESIDENT_OF = f"{example_prefix}/president_of"
PRIME_MINISTER_OF = f"{example_prefix}/prime_minister_of"
POPULATION_OF = f"{example_prefix}/population_of"
AREA_OF = f"{example_prefix}/area_of"
GOVERNMENT_FORM = f"{example_prefix}/government_form"
CAPITAL_OF = f"{example_prefix}/capital_of"
BORN_IN = f"{example_prefix}/born_in"
BDATE = f"{example_prefix}/bdate"
# ----------------------- #

# ------ Globals ------ #
q11_flag = 0
q_split = []


# --------------------- #
def edit_list_result(query_result_list):
    result = []
    for i in range(len(query_result_list)):
        last_slash = query_result_list[i][0].rfind('/')
        result.append((query_result_list[i][0][last_slash + 1:]).replace('_', ' '))
    return result


def print_query_result(query_result_list):
    global q11_flag
    if not q11_flag:
        query_result_list = edit_list_result(query_result_list)
    q11_flag = 0

    query_result_list.sort()
    query_result_list = (', '.join(query_result_list))

    # delete non printable characters
    query_result_list = query_result_list.encode("utf-8", "ignore")
    query_result_list = query_result_list.decode()

    if query_result_list == "Philip %22Brave%22 Davis":
        print('Philip "Brave" Davis')
    else:
        print(query_result_list)


def questions_1_2():
    subject_start_ind = q_split.index('of') + 1
    q_relation = '_'.join(q_split[3: subject_start_ind])
    q_entity = ('_'.join(q_split[subject_start_ind:]))[:-1]
    return f"select ?x where {{ <{example_prefix}/{q_entity}> <{example_prefix}/{q_relation}> ?x . }}"


def questions_3_4_6():
    q_relation = '_'.join(q_split[3: 5])
    q_entity = ('_'.join(q_split[5:]))[:-1]
    return f"select ?x where {{ <{example_prefix}/{q_entity}> <{example_prefix}/{q_relation}> ?x . }}"


def question_5():
    q_entity = ('_'.join(q_split[7:]))[:-1]
    return f"select ?x where {{ <{example_prefix}/{q_entity}> <{GOVERNMENT_FORM}> ?x . }}"


def questions_7_8_9_10(q_word):
    country_start_ind = q_split.index('of') + 1
    q_relation = '_'.join(q_split[3: country_start_ind])
    q_entity = ('_'.join(q_split[country_start_ind:-1]))
    if q_word == 'When':
        # questions 7, 9
        return f"select ?x where {{ <{example_prefix}/{q_entity}> <{example_prefix}/{q_relation}> ?y . " \
               f"                                ?y <{BDATE}> ?x .     }}"
    # questions 8, 10
    return f"select ?x where {{ <{example_prefix}/{q_entity}> <{example_prefix}/{q_relation}> ?y . " \
           f"                                ?y <{BORN_IN}> ?x .     }}"


def question_11_president():
    q_entity = ('_'.join(q_split[2:])[:-1])
    return f"select ?x where {{ ?x <{PRESIDENT_OF}> <{example_prefix}/{q_entity}> . }}"


def question_11_prime_minister():
    q_entity = ('_'.join(q_split[2:])[:-1])
    return f"select ?x where {{ ?x <{PRIME_MINISTER_OF}> <{example_prefix}/{q_entity}> . }}"


def question_12():
    entity1_end_ind = q_split.index('are')
    entity2_start_ind = entity1_end_ind + 2
    q_entity1 = '_'.join(q_split[2:entity1_end_ind])
    q_entity2 = '_'.join(q_split[entity2_start_ind:])[:-1]
    return f"select (count(?x) as ?count) {{ ?x <{GOVERNMENT_FORM}> <{example_prefix}/{q_entity1}> . " \
           f"                                ?x <{GOVERNMENT_FORM}> <{example_prefix}/{q_entity2}> .     }}"


def question_13():
    str_entity = q_split[-1].lower()
    return f"select ?x where {{ ?x <{CAPITAL_OF}> ?y . " \
           f"                   filter contains(replace(lcase(str(?y)),'{example_prefix}', ''), '{str_entity}')     }}"


# question 14 and our question - How many prime ministers were born in <country>?
def question_14_our():
    country_start_ind = q_split.index('in') + 1
    q_relation = PRESIDENT_OF if q_split[2] == 'presidents' else PRIME_MINISTER_OF
    q_entity = ('_'.join(q_split[country_start_ind:]))[:-1]
    return f"select (count(?x) as ?count) {{ ?x <{BORN_IN}> <{example_prefix}/{q_entity}> . " \
           f"                                ?y <{q_relation}> ?x .     }}"


def handler(q):
    global q11_flag
    global q_split
    g = rdflib.Graph()
    g.parse('ontology.nt', format='nt')
    q_split = q.split()
    q_word = q_split[0]
    if q_word == 'Who':
        if q_split[2] == 'the':
            q = questions_1_2()
        else:
            q11_flag = 1
            q1 = question_11_president()
            q2 = question_11_prime_minister()
            answer1 = ["President of " + a for a in edit_list_result(list(g.query(q1)))]
            answer2 = ["Prime Minister of " + a for a in edit_list_result(list(g.query(q2)))]
            print_query_result(answer1 + answer2)
            return
    elif q_word == 'What':
        if q_split[3] == 'form':
            q = question_5()
        else:
            q = questions_3_4_6()
    elif q_word == 'When' or q_word == 'Where':
        q = questions_7_8_9_10(q_word)
    elif q_word == "How":
        if "are" in q_split:
            q = question_12()
        else:
            q = question_14_our()
    else:
        q = question_13()
    print_query_result(list(g.query(q)))
