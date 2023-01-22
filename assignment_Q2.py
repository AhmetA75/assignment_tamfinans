import random
from redis import Redis
from redisgraph import Node, Edge, Graph
from faker import Faker
from time import time
import ujson
import copy
import numpy as np
from numpy.linalg import norm
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6479
REDIS_GRAPH = "case_graph"
fake_generator = Faker(locale="tr")

products = {
    "phone": 100,
    "laptop": 300,
    "dress": 20,
    "pencil": 2,
    "watch": 50
}
product_list = list(products.keys())


def control_user_exist(redis_graph, phone_number='76756765756'):
    query = f"MATCH (p:person) WHERE p.phone='{phone_number}' RETURN ID(p), p.name"

    result = redis_graph.query(query)

    return result.is_empty()


def create_test_graph():
    # insert_products(product_dict=products)

    r = Redis(host=REDIS_HOST, port=REDIS_PORT)

    redis_graph = Graph(REDIS_GRAPH, r)

    try:
        redis_graph.delete()
    except Exception as err:
        print(err)
        pass

    person_node = Node(label='person', properties={"name": "ahmet", "phone": "76756765756"})
    person2_node = Node(label='person', properties={"name": "mahmut", "phone": "5600594585"})
    pro_node = Node(label='product', properties={"name": "elma", "price": 2.9})
    redis_graph.add_node(person_node)
    redis_graph.add_node(person2_node)
    redis_graph.add_node(pro_node)

    edge = Edge(person_node, 'buy', pro_node, properties={'count': 1})
    edge_2 = Edge(person_node, 'add_cart', pro_node, properties={'count': 3})
    edge_3 = Edge(person2_node, 'add_cart', pro_node, properties={'count': 5})

    redis_graph.add_edge(edge_2)
    redis_graph.add_edge(edge)
    redis_graph.add_edge(edge_3)

    redis_graph.commit()

    r.close()


def clear_graph():
    """
    clear redis graph
    :return:
    """
    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis_graph = Graph(REDIS_GRAPH, r)

    try:
        redis_graph.delete()
    except Exception as err:
        print(err)
        pass
    r.close()


def write_json(filename, data):
    """
    writes dict object to json file
    :param filename: file path
    :param data: dict object
    :return:
    """
    # Serializing json
    json_object = ujson.dumps(data, indent=2)

    # Writing to sample.json
    with open(filename, "w") as outfile:
        outfile.write(json_object)
        outfile.close()


def rand_product(product_list=None, cart_limit=5):
    """
    This function generates random amount of buying and carting distinct items
    :param product_list: Available items for buying
    :param cart_limit: Max cart limit for items
    :return: Returns carted and bought items in dictionary
    """
    if product_list is None:
        product_list = ["tel", "pc", "elbise", "kalem", "saat"]

    # generate random item count
    item_count = random.randint(0, len(product_list))
    # print(item_count)

    # generate random distinct index list
    control_count = 0
    index_list = []
    product_dict = {}
    while control_count < item_count:
        random_index = random.randint(0, len(product_list) - 1)
        if random_index not in index_list:
            index_list.append(random_index)
            product_dict[product_list[random_index]] = {"cart": 0, "buy": 0}  # init dict
            control_count += 1

    # generate random cart and buy numbers for each product
    for item in product_dict:
        cart_number = random.randint(1, cart_limit)
        buy_number = random.randint(0, cart_number)

        product_dict[item]["cart"] = cart_number
        product_dict[item]["buy"] = buy_number

    print(product_dict)
    return product_dict


def insert_products(product_dict):
    """
    insert products with prices to the redis graph
    :param product_dict:
    :return:
    """

    r = Redis(host=REDIS_HOST, port=REDIS_PORT)

    redis_graph = Graph(REDIS_GRAPH, r)

    # redis_graph.delete()

    product_id = 0

    for product in product_dict:
        product_node = Node(label='product', properties={"id": product_id, "name": product,
                                                         "price": product_dict[product]})
        redis_graph.add_node(product_node)
        product_id += 1

    redis_graph.commit()

    r.close()


def create_user(redis_graph, person_id, fake=fake_generator):
    """
    creates user and inserts it into redis graph with unique phone number and unique id
    :param redis_graph: redis graph object
    :param person_id: person id
    :param fake: faker object
    :return: phone number
    """
    # generate phone number for new user
    phone_number = fake.phone_number()

    # generate phone numbers until number is unique (not in graph)
    while not control_user_exist(redis_graph=redis_graph, phone_number=phone_number):
        phone_number = fake.phone_number()

    # generate name and age for user
    user_name = fake.name()
    # age = random.randint(20, 60)

    # add person node
    person_node = Node(label='person', properties={"id": person_id, "name": user_name, "phone": phone_number})
    redis_graph.add_node(person_node)

    return phone_number


def create_all_users(user_count):
    """
    creates users and user actions and inserts them into redis graph
    :param user_count: number of users
    :return:
    """
    all_phone_numbers = []

    redis_connection = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis_graph = Graph(REDIS_GRAPH, redis_connection)

    person_id = 0

    for i in range(user_count):
        print(i)
        user_phone = create_user(redis_graph=redis_graph, person_id=person_id)
        all_phone_numbers.append(user_phone)
        person_id += 1

    # commit changes
    redis_graph.commit()

    for number in all_phone_numbers:

        # get product dict for person
        pr_dict = rand_product(product_list=product_list)

        # add edges for products
        for product in pr_dict:
            # add cart edge
            add_cart_query = """MATCH (p:person), (pr:product) WHERE p.phone = '%s' and pr.name = '%s'
             CREATE (p)-[:add_cart {count:'%s'}]->(pr)""" % (number, product, pr_dict[product]["cart"])
            redis_graph.query(add_cart_query)

            # add buy edge if count is greater than 0
            if pr_dict[product]["buy"] != 0:
                add_buy_query = """MATCH (p:person), (pr:product) WHERE p.phone = '%s' and pr.name = '%s'
                         CREATE (p)-[:buy {count:'%s'}]->(pr)""" % (number, product, pr_dict[product]["buy"])
                redis_graph.query(add_buy_query)

    redis_connection.close()


def get_data_batch(redis_graph, user_dict, offset, page_size, product_list):
    """
    get user and user actions data in batch
    :param redis_graph: redis graph object
    :param user_dict: all user ids and their actions
    :param offset: pointer for all redis data
    :param page_size: batch size
    :param product_list: product names
    :return: user_dict and boolean value(True if data is still exist in redis),
    """
    query = """MATCH (p:person)-[v:add_cart|buy]->(pr:product) 
    RETURN p.id, v.count, pr.name, TYPE(v) SKIP %s LIMIT %s""" % (offset, page_size)

    result = redis_graph.query(query)

    # return if result is empty
    if result.is_empty():
        return user_dict, False

    for record in result.result_set:
        """
        record 0 => Person ID
        record 1 => Product Count
        record 2 => Product Name
        record 3 => Action Type
        """
        user_id = record[0]
        pr_count = record[1]
        pr_name = record[2]
        act_type = record[3]

        # create user if it not exists
        if user_id not in user_dict:

            empty_product_dict = dict()
            for product in product_list:
                empty_product_dict[product] = 0

            user_dict[user_id] = dict()
            user_dict[user_id]["buy"] = copy.deepcopy(empty_product_dict)
            user_dict[user_id]["add_cart"] = copy.deepcopy(empty_product_dict)

        user_dict[user_id][act_type][pr_name] += int(pr_count)

    return user_dict, True


def create_user_json(product_list, page_size=100):
    """
    get all user data and create json file
    :param product_list: product names
    :param page_size: batch size
    :return:
    """

    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis_graph = Graph(REDIS_GRAPH, r)

    is_full = True
    offset = 0
    user_dict = {}

    while is_full:
        print(f'OFFSET = {offset}')
        user_dict, is_full = get_data_batch(redis_graph=redis_graph, user_dict=user_dict, offset=offset,
                                            page_size=page_size, product_list=product_list)
        offset += page_size

    write_json(filename="data/users.json", data=user_dict)
    r.close()


def analyze(file: str) -> None:
    """
    find similarities between all person nodes with using Cosine Similarity Method
    :param file: contains collected graph data
    :return:
    """

    r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis_graph = Graph(REDIS_GRAPH, r)

    with open(f"data/{file}", "r") as f:  # read json file
        json_data = json.load(fp=f)
    f.close()

    ids = list(json_data.keys())  # get person keys to analyze
    traverse = list(json_data.keys())  # traversing ids (except current person id)

    for pid in ids:
        pobj = json_data[pid]  # current person id
        p_add_list = list(pobj["add_cart"].values())  # person's (with pid) add cart data
        p_buy_list = list(pobj["buy"].values())  # person's (with pid) buy data

        traverse.remove(pid)  # remove current pid from traversal points (to avoid duplicate)
        for tid in traverse:
            tobj = json_data[tid]  # iterate through traversal person nodes
            t_add_list = list(tobj["add_cart"].values())  # destination person add cart
            t_buy_list = list(tobj["buy"].values())  # destination person buy

            add_cosine = np.dot(p_add_list, t_add_list) / (
                        norm(p_add_list) * norm(t_add_list))  # cosine sim between add cart data
            buy_cosine = np.dot(p_buy_list, t_buy_list) / (
                        norm(p_buy_list) * norm(t_buy_list))  # cosine sim between buy data

            if np.isnan(add_cosine):
                add_cosine = 0
            if np.isnan(buy_cosine):
                buy_cosine = 0

            similarity = (add_cosine * 0.3) + (buy_cosine * 0.7)  # coefficients: for buy => 0.7, add => 0.3

            result = redis_graph.query("""MATCH (p:person), (pr:person) WHERE p.id = %s and pr.id = %s
                                          RETURN ID(p), ID(pr)""" % (pid, tid))  # find redis graph ids
            id0 = result.result_set[0][0]  # get real (redis graph) id using id property
            id1 = result.result_set[0][1]  # get second real (redis graph) id using id property
            # print(f"pid => {pid}, tid => {tid}")
            # print(f"ID1 => {id0}, ID2 => {id1}")
            # print(f"SIMI => {similarity}, add_cos {add_cosine}, buy_cos {buy_cosine}")
            redis_graph.query("""MATCH (p:person), (pr:person) WHERE ID(p) = %s and ID(pr) = %s 
                                 CREATE (p)-[:similarity {rate:%.2f}]->(pr)""" % (
                id0, id1, similarity))  # add edge query
            # print("uyu")
            # sleep(0.5)

    r.close()


if __name__ == '__main__':
    # remove graph
    clear_graph()
    # add products to the graph
    insert_products(product_dict=products)
    # add users and their edges with products to the graph
    start = time()
    create_all_users(user_count=100)
    print(f"Exec time => {time() - start}")
    # fetch all data from redis
    create_user_json(product_list=product_list, page_size=10)
    start = time()
    analyze(file="users.json")
    print(f"Exec time => {time() - start}")
