from db_handler import DBHandler
import copy

"""
Ignore functions here just used for testing
"""


def similarity(person_a, person_b, both_reviewed):
    average_of_a = get_average(person_a)
    average_of_b = get_average(person_b)

    import math
    top = 0
    bot1 = 0
    bot2 = 0
    for item in both_reviewed:
        top += (person_a[item] - average_of_a) * (person_b[item] - average_of_b)
        bot1 += (person_a[item] - average_of_a) ** 2
        bot2 += (person_b[item] - average_of_b) ** 2

    if bot1 == 0 or bot2 == 0:
        return 0
    pearson = top / (math.sqrt(bot1) * math.sqrt(bot2))
    return pearson


def create_neighbourhood(user_info, no_longer_ignored,average_for_item):
    print(len(user_info))
    predictions = []
    for person_a, info in user_info.items():
        neighbour = {}
        if int(person_a) % 5000 == 0:
            print("on person " + person_a)
        for person_b, i2 in user_info.items():
            if person_b == person_a:
                continue
            both_reviewed = get_both_reviewed(user_info[person_a], user_info[person_b])

            if len(both_reviewed) < 21:
                continue

            if similarity(user_info[person_a], user_info[person_b], both_reviewed) > 0.9999:
                neighbour[person_b] = i2

            if len(neighbour) > 101:
                break

        predictions.append(predict(person_a, user_info[person_a], neighbour,average_for_item))

    no_longer_ignored.append(predictions)


def get_both_reviewed(person_a, person_b):
    both_reviewed = []
    for k, v in person_a.items():
        if k in person_b:
            both_reviewed.append(k)
    return both_reviewed


def get_average(person_a):
    return sum([float(v) for k, v in person_a.items()]) / len(person_a.items())


def predict(userid, user, neighbourhood,average_for_item):
    average_of_user = get_average(user)
    predict_items = [k for k, v in user.items()]
    top = 0
    bot = 0
    for item in predict_items:
        for k, v in neighbourhood.items():
            if item not in v:
                continue
            top += similarity(user, v, get_both_reviewed(v, user)) * (v[item] - get_average(v))
            bot += similarity(user, v, get_both_reviewed(v, user))
        if top == 0 or bot == 0:
            return userid, item, user[item], round(average_for_item[item] * 2) / 2

        pred = average_of_user + (top / bot)
        pred_2 = round(pred * 2) / 2

        return userid, item, user[item], pred_2


def split_dict_to_multiple(input_dict, max_limit):
    """Splits dict into multiple dicts with given maximum size.
        Returns a list of dictionaries."""

    chunks = []
    curr_dict = {}
    for k, v in input_dict.items():
        if len(curr_dict.keys()) < max_limit:
            curr_dict.update({k: v})
        else:
            chunks.append(copy.deepcopy(curr_dict))
            curr_dict = {k: v}
    # update last curr_dict
    chunks.append(curr_dict)
    return chunks


def runner():
    db = DBHandler()
    db.setup_test_table()

    user_info = {}
    for x in db.read_data("comp3208-train-small.csv"):
        listParts = x.strip().split(',')
        if listParts[2] == "rating":
            continue
        if listParts[0] in user_info:
            user_info[listParts[0]][listParts[1]] = float(listParts[2])
        else:
            user_info[listParts[0]] = {listParts[1]: float(listParts[2])}

    average_for_item = {}
    for k,v in user_info.items():
        for k2,v2 in v.items():
            if k2 in average_for_item:
                average_for_item[k2].append(v2)
            else:
                average_for_item[k2] = [v2]

    for k in average_for_item.keys():
        average_for_item[k] = sum(average_for_item[k])/len(average_for_item[k])

    import os
    from multiprocessing import Process, Manager

    x = split_dict_to_multiple(user_info, len(user_info.keys()) / (os.cpu_count() - 1))
    results = Manager().list()
    processes = []
    for i in range(0, 11):
        p = Process(target=create_neighbourhood, args=(x[i], results,average_for_item))
        processes.append(p)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("DONE ADDING")

    for x in results:
        for y in x:
            db.insert_into_test_table(y[0], y[1], y[2], y[3])

    db.calculate_test_mse()

if __name__ == '__main__':
    runner()
