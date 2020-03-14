import datetime as dt
import os
import ssl
import requests
from collections import defaultdict

api_base = "https://json.medrating.org"
api_user = "{}/users".format(api_base)
api_todos = "{}/todos".format(api_base)
# Certificate verify hack for MacOS with embedded version of OpenSSL,
# which does not use the system certificate store by default
# This is the Way:
# /Applications/Python\ 3.7/Install Certificates.command
context = ssl._create_unverified_context()

completed = defaultdict(list)
uncompleted = defaultdict(list)
uncompleted_title_max_length = 50
out_dir='tasks'

def get_data(api_user, api_todos):
    users = requests.get(api_user).json()
    todos = requests.get(api_todos).json()
    return users, todos

def make_report_for_all_users(users, tasks):
    for task in tasks:
        if task['completed']:
            completed[task['userId']].append(task['title'])
        else:
            uncompleted[task['userId']].append(task['title'])
    return completed, uncompleted


def generate_user_reports(max_length = 50):
    users, tasks = get_data(api_user, api_todos)
    completed_tasks, uncompleted_tasks = make_report_for_all_users(users, tasks)

    try:
        os.makedirs('tasks', exist_ok=True)
    except:
        raise OSError("Can't create destination directory tasks!")
    os.chdir(out_dir)

    time_now = dt.datetime.now().strftime("%d.%m.%Y %H:%M")

    for user in users:
        user_key = user["id"]
        username = user["username"]

        if len(completed_tasks[user_key]) and len(uncompleted_tasks[user_key]) == 0:
            continue

        uncompleted_tasks_formatted = [
            (task[:max_length] + '...') 
            if len(task) > max_length
            else task 
            for task in uncompleted_tasks[user_key]
        ]

        if os.path.isfile(f'{username}.txt'):
            creation_time = os.path.getctime(f'{username}.txt')
            formatted_ctime = dt.datetime.fromtimestamp(
                creation_time).strftime('%Y-%m-%dT%H:%M')
            os.rename(f'{username}.txt',
                      f'{username}_{formatted_ctime}.txt')
        try:
            with open(f'{username}.txt', 'w') as f:
                newline = '\n'
                f.write(
                    f"""{user["name"]} <{user["email"]}> {time_now}
{user["company"]["name"]}

Завершённые задачи:
{newline.join(completed_tasks[user_key])}

Оставшиеся задачи:
{newline.join(uncompleted_tasks_formatted)}"""
                )
        except:
            try:
                os.remove(f'{username}.txt')
                print(
                    f'Cant write to {username}.txt new file removed successfully')
            except OSError as e:
                if e.errno == ENOENT:
                    # suppress "FileNotFoundError"
                    pass
                else:
                    raise
            os.rename(f'{username}_{formatted_ctime}.txt',
                      f'{username}.txt')
            raise


if __name__ == '__main__':
    generate_user_reports(max_length=uncompleted_title_max_length)
