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
            x["title"]
            for x in tasks
            if x["userId"] == user["id"] and x["completed"]
        ]
        uncompleted_tasks = [
            x["title"] if len(x["title"]) < 50
            else x["title"][:50]+'...'
            for x in tasks
            if x["userId"] == user["id"] and not x["completed"]
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
            os.rename(f'{user["username"]}_{formatted_time}.txt', f'{user["username"]}.txt'
                      )
            print("An IOError has occurred!")


if __name__ == '__main__':
    generate_reports()
