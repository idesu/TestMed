import datetime as dt
import os
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
    all_completed_tasks = defaultdict(list)
    all_uncompleted_tasks = defaultdict(list)
    for task in todos:
        if task['completed']:
            all_completed_tasks[task['userId']].append(task['title'])
        else:
            all_uncompleted_tasks[task['userId']].append(task['title'])
    return all_completed_tasks, all_uncompleted_tasks


def format_report(user, user_completed, user_uncompleted):
    def format_title(title):
        if len(title) <= MAX_TASK_TITLE_LEN:
            return title
        return title[:MAX_TASK_TITLE_LEN] + '...'

    user_completed = [format_title(title) for title in user_completed]
    user_uncompleted = [format_title(title) for title in user_uncompleted]
    now_time = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    newline = '\n'

    return (f"""{user["name"]} <{user["email"]}> {now_time}
{user["company"]["name"]}

Завершённые задачи:
{newline.join(user_completed)}

Оставшиеся задачи:
{newline.join(user_uncompleted)}
""")


def save_report_to_file(user, user_completed, user_uncompleted):
    if not user_completed and not user_uncompleted:
        return

    report_name = f"{OUT_DIR}/{user['username']}.txt"

    try:
        with open(report_name, "r") as f:
            prev_date = f.readline().rstrip().rsplit(None, 2)[-2:]
    except (OSError, IOError) as e:
        prev_date = None

    with open(f"{report_name}.new", "w") as f:
        f.write(format_report(user, user_completed, user_uncompleted))

    if prev_date:
        date_fname = dt.datetime.strptime(
            ' '.join(prev_date),
            "%d.%m.%Y %H:%M"
        ).strftime("%Y-%m-%dT%H:%M")
        os.rename(
            report_name,
            f"{OUT_DIR}/{user['username']}_{date_fname}.txt"
        )
    os.rename(f"{report_name}.new", report_name)


def full_report(users, all_completed_tasks, all_uncompleted_tasks):
    for user in users:
        save_report_to_file(
            user,
            all_completed_tasks.get(user['id'], []),
            all_uncompleted_tasks.get(user['id'], [])
        )

    all_ids = set([user['id'] for user in users])
    completed_ids = set(all_completed_tasks.keys())
    uncompleted_ids = set(all_uncompleted_tasks.keys())

    if all_ids == completed_ids.union(uncompleted_ids):
        return

    print("== Extra ==")
    print("Users with no tasks: ")
    print(", ".join(list(all_ids.difference(
        completed_ids.union(uncompleted_ids)))))
    print("User ids from task with no user description: ")
    print(", ".join(list(
        completed_ids.union(uncompleted_ids).difference(all_ids)
    )))


def main():
    users = get_data(API_USERS)
    todos = get_data(API_TODOS)
    all_completed_tasks, all_uncompleted_tasks = (
        make_report_for_all_users(todos)
    )

    try:
        os.makedirs(OUT_DIR, exist_ok=True)
    except:
        raise OSError("Can't create destination directory tasks!")

    full_report(users, all_completed_tasks, all_uncompleted_tasks)


if __name__ == '__main__':
    main()
