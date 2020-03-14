import datetime as dt
import json
import os
import ssl
import urllib.request

todos_url = "https://json.medrating.org/todos"
users_url = "https://json.medrating.org/users"
# Certificate verify hack for MacOS with embedded version of OpenSSL,
# which does not use the system certificate store by default
# This is the Way:
# /Applications/Python\ 3.7/Install Certificates.command
context = ssl._create_unverified_context()


def generate_reports():
    time_now = dt.datetime.now().strftime("%d.%m.%Y %H:%M")

    with urllib.request.urlopen(users_url, context=context) as url:
        users = json.loads(url.read().decode())

    with urllib.request.urlopen(todos_url, context=context) as url:
        tasks = json.loads(url.read().decode())

    os.makedirs('tasks', exist_ok=True)
    os.chdir('tasks')

    for user in users:
        completed_tasks = [
            task["title"]
            for task in tasks
            if task["userId"] == user["id"] and task["completed"]
        ]
        task_title_max_length = 50
        uncompleted_tasks = [
            task["title"] if len(task["title"]) < task_title_max_length
            else task["title"][:task_title_max_length]+'...'
            for task in tasks
            if task["userId"] == user["id"] and not task["completed"]
        ]

        if len(uncompleted_tasks) and len(completed_tasks) == 0:
            continue

        username = user["username"]

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
{newline.join(completed_tasks)}

Оставшиеся задачи:
{newline.join(uncompleted_tasks)}"""
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


if __name__ == '__main__':
    generate_reports()
