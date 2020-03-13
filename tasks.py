import datetime as dt
import json
import os
import urllib.request


todos_url = "https://json.medrating.org/todos"
users_url = "https://json.medrating.org/users"

time_now = dt.datetime.now().strftime("%d.%m.%Y %H:%M")

with urllib.request.urlopen(users_url) as url:
    users = json.loads(url.read().decode())

with urllib.request.urlopen(todos_url) as url:
    tasks = json.loads(url.read().decode())


def generate_reports():
    try:
        os.makedirs('tasks', exist_ok=True)
    except:
        raise OSError("Can't create destination directory tasks!")

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

        if os.path.isfile(f'{user["username"]}.txt'):
            creation_time = os.path.getctime(f'{user["username"]}.txt')
            formatted_time = dt.datetime.fromtimestamp(
                creation_time).strftime('%Y-%m-%dT%H:%M')
            os.rename(f'{user["username"]}.txt',
                      f'{user["username"]}_{formatted_time}.txt')

        try:
            with open(f'{user["username"]}.txt', 'w') as f:
                newline = '\n'
                f.write(
                    f"""{user["name"]} <{user["email"]}> {time_now}
{user["company"]["name"]}

Завершённые задачи:
{newline.join(completed_tasks)}

Оставшиеся задачи:
{newline.join(uncompleted_tasks)}"""
                )
        except IOError:
            os.rename(f'{user["username"]}_{formatted_time}.txt',
                      f'{user["username"]}.txt'
                      )
            print("An IOError has occurred!")


if __name__ == '__main__':
    generate_reports()
