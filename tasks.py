import datetime as dt
import os
import ssl
from collections import defaultdict

import requests

API_BASE = "https://json.medrating.org"
API_USERS = f"{API_BASE}/users"
API_TODOS = f"{API_BASE}/todos"
MAX_TASK_TITLE_LEN = 50
OUT_DIR = 'tasks'


def get_data(url):
    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def make_report_for_all_users(todos):
    completed = defaultdict(list)
    uncompleted = defaultdict(list)
    for task in todos:
        if task['completed']:
            completed[task['userId']].append(task['title'])
        else:
            uncompleted[task['userId']].append(task['title'])
    return completed, uncompleted


def format_report(user, completed, uncompleted):
    def format_title(title):
        if len(title) <= MAX_TASK_TITLE_LEN:
            return title
        return title[:MAX_TASK_TITLE_LEN] + '...'
    
    completed = [format_title(title) for title in completed]
    uncompleted = [format_title(title) for title in uncompleted]
    now_time = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    newline = '\n'
    
    return (
f"""{user["name"]} <{user["email"]}> {now_time}
{user["company"]["name"]}

Завершённые задачи:
{newline.join(completed)}
    
Оставшиеся задачи:
{newline.join(uncompleted)}
"""
)

def save_report_to_file(user, completed, uncompleted):
    if not completed and not uncompleted:
        return

    report_name = f"{OUT_DIR}/{user['username']}.txt"

    try:
        with open(report_name, "r") as f:
            prev_date = f.readline().rstrip().rsplit(None, 2)[-2:]
    except (OSError, IOError) as e:
        prev_date = None
    
    with open(f"{report_name}.new", "w") as f:
        f.write(format_report(user, completed, uncompleted))

    if prev_date:
        date_fname = dt.datetime.strptime(
            prev_date[0] + " " + prev_date[1],
            "%d.%m.%Y %H:%M"
        ).strftime("%Y-%m-%dT%H:%M")
        os.rename(
            report_name,
            f"{OUT_DIR}/{user['username']}_{date_fname}.txt"
        )
    os.rename(f"{report_name}.new", report_name)



def full_report(users, all_users_completed, all_users_uncompleted):
    for user in users:
        save_report_to_file(
            user,
            all_users_completed.get(user['id'], []),
            all_users_uncompleted.get(user['id'], [])
        )

    all_users_ids = set([user['id'] for user in users])
    completed_ids = set(all_users_completed.keys())
    uncompleted_ids = set(all_users_uncompleted.keys())

    if all_users_ids == completed_ids.union(uncompleted_ids):
        return

    print("== Extra ==")
    print("Users with no tasks: ")
    print(", ".join(list(all_users_ids.difference(
        completed_ids.union(uncompleted_ids)))))
    print("User ids from task with no user description: ")
    print(", ".join(list(completed_ids.union(uncompleted_ids).difference(all_users_ids))))


def main():
    users = get_data(API_USERS)
    todos = get_data(API_TODOS)
    all_users_completed, all_users_uncompleted = make_report_for_all_users(todos)

    try:
        os.makedirs(OUT_DIR, exist_ok=True)
    except:
        raise OSError("Can't create destination directory tasks!")

    full_report(users, all_users_completed, all_users_uncompleted)


if __name__ == '__main__':
    main()
