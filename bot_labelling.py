import random, os
import pandas as pd

print("loading comments...")
bot_comments = pd.read_csv("bot_comments_text.csv")
authors = sorted(bot_comments.author.unique())
num_to_check = round(len(bot_comments.author.unique())/4)

who = {"jon":0,"ben":1,"akio":2,"yi":3}
who_is_checking = input("who is this? (jon/ben/akio/yi):")
offset = 576 * who[who_is_checking]
users_to_check = authors[offset:offset+num_to_check]

try:
    results = pd.read_csv("{}_results.csv".format(who_is_checking))
    print("results so far:",results)
    results = results.to_dict('records')
    already_checked = [x['user'] for x in results]
    print("checked:",already_checked)
except Exception as e:
    print("ERR:",e)
    results = []
    already_checked = []

for user,data in bot_comments.groupby("author"):
    if user in users_to_check and user not in already_checked:
        print("-"*40)
        print()
        print("-"*40)
        print(user)
        comments= list(data.body.values)
        for x in random.sample(comments, min(20, len(comments))):
            try:
                print(x)
            except:
                pass
        determination = input("({} of {}):".format(len(results)+1,len(users_to_check)))
        if determination == "exit" or determination == "quit":
            break
        results.append({
            "user":user,
            "label":determination
        })
        results_df = pd.DataFrame(results)
        results_df.set_index("user")
        results_df.to_csv("{}_results.csv".format(who_is_checking), index=None)
