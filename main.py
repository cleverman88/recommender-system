from db_handler import DBHandler
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


def create_neighbourhood(user_info,db):
    print(len(user_info))
    for person_a, info in user_info.items():
        neighbour = {}
        all_items = set([k for k, v in info.items()])
        print("Predicting for " + person_a)
        for person_b, i2 in user_info.items():
            if person_b == person_a:
                continue
            both_reviewed = get_both_reviewed(user_info[person_a], user_info[person_b])

            if similarity(user_info[person_a], user_info[person_b], both_reviewed) > 0.5:
                neighbour[person_b] = i2
                for x in [k for k, v in i2.items()]:
                    if x in all_items:
                        all_items.remove(x)

            if len(neighbour) < 5 and len(all_items) == 0:
                break

        predict(person_a,user_info[person_a], neighbour,db)

    db.calculate_test_mse()


def get_both_reviewed(person_a, person_b):
    both_reviewed = []
    for k, v in person_a.items():
        if k in person_b:
            both_reviewed.append(k)
    return both_reviewed


def get_average(person_a):
    return sum([float(v) for k, v in person_a.items()]) / len(person_a.items())


def predict(userid, user, neighbourhood,db):
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

        pred = average_of_user + (top / bot)
        db.insert_into_test_table(userid,item,user[item],pred)


if __name__ == '__main__':
    db = DBHandler()
    db.setup_test_table()
    #
    # user_info = {}
    # for x in db.read_data("comp3208-train-small.csv"):
    # 	listParts = x.strip().split(',')
    # 	if listParts[2] == "rating":
    # 		continue
    # 	if listParts[0] in user_info:
    # 		user_info[listParts[0]][listParts[1]] = float(listParts[2])
    # 	else:
    # 		user_info[listParts[0]] = {listParts[1]: float(listParts[2])}
    #
    # print(similarity(user_info["1"], user_info["2"], get_both_reviewed(user_info["1"], user_info["2"])))
    # print(user_info["6"])
    # create_neighbourhood(user_info,db)
