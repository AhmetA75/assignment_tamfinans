from redis import Redis
from redisgraph import Graph
import random

REDIS_HOST = "localhost"
REDIS_PORT = 6479
REDIS_GRAPH = "case_graph"


def get_person_products(redis_graph, person_id):
    """

    :param redis_graph:
    :param person_id:
    :return:
    """
    product_query = """MATCH (p:person {id: %s})-[v:buy]->(pr:product)
               RETURN pr.name""" % person_id

    product_result = redis_graph.query(product_query)

    # get all products that bought from person into product_list
    product_list = []
    for record in product_result.result_set:
        product_list.append(record[0])

    return product_list


def get_similar_persons(redis_graph, person_id, person_limit):
    """

    :param redis_graph:
    :param person_id:
    :param person_limit:
    :return:
    """
    similarity_query = """MATCH (p:person {id: %s})-[v:similarity]->(pr:person)
            RETURN pr.id, v.rate ORDER BY v.rate DESC LIMIT %s""" % (person_id, person_limit)

    similarity_result = redis_graph.query(similarity_query)

    # get most similar person ids
    person_dict = {}
    for record in similarity_result.result_set:
        person_dict[record[0]] = record[1]

    print(person_dict)
    return person_dict


def recommend_product(person_id, person_limit=5):
    """

    :param person_id:
    :param person_limit:
    :return:
    """
    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis_graph = Graph(REDIS_GRAPH, r)

    # get all products that bought from person into product_list
    product_list = get_person_products(redis_graph=redis_graph, person_id=person_id)

    # get most similar person ids
    person_dict = get_similar_persons(redis_graph=redis_graph, person_id=person_id, person_limit=person_limit)

    for similar_person_id in person_dict.keys():
        similar_person_products = get_person_products(redis_graph=redis_graph, person_id=similar_person_id)

        difference_list = list(set(similar_person_products) - set(product_list))

        if difference_list:
            return difference_list[random.randint(0, (len(difference_list) - 1))], person_dict[similar_person_id]
        else:
            print("List is empty. Moving for next similar person.")

    return None, None


if __name__ == '__main__':
    person_id = 11
    recommended_product, recommend_rate = recommend_product(person_id=person_id)

    if recommended_product is not None:
        print(f"\nRecommended product for person with Person ID = {person_id} is ==> {recommended_product}"
              f"\nRecommendation rate = %{int(100 * recommend_rate)}")
    else:
        print(f"Recommendation failed! Person with Person ID = {person_id} already bought most of products !")
