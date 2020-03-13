import urllib.request
import json
import os
import datetime as dt


todos_url = "https://json.medrating.org/todos"
users_url = "https://json.medrating.org/users"
time_now = dt.datetime.now()


users = json.loads(urllib.request.urlopen(users_url).read())
tasks = json.loads(urllib.request.urlopen(todos_url).read())


os.makedirs('tasks', exist_ok=True)


def generate_reports():
    for user in users:
        completed_tasks = [
            x["title"]+'\n'
            for x in tasks
            if x["userId"] == user["id"] and x["completed"]
        ]
        uncompleted_tasks = [
            x["title"]+'\n' if len(x["title"]) < 50
            else x["title"][:50]+'...\n'
            for x in tasks
            if x["userId"] == user["id"] and not x["completed"]
        ]

        if os.path.isfile(f'tasks/{user["username"]}.txt'):
            creation_time = os.path.getctime(f'tasks/{user["username"]}.txt')
            formatted_time = dt.datetime.fromtimestamp(
                creation_time).strftime('%Y-%m-%dT%H:%M')
            os.rename(f'tasks/{user["username"]}.txt',
                      f'tasks/{user["username"]}_{formatted_time}.txt')

        try:
            with open(f'tasks/{user["username"]}.txt', 'w') as f:
                f.write(
                    f'{user["name"]} <{user["email"]}> {time_now.strftime("%d.%m.%Y %H:%M")}\n')
                f.write(f'{user["company"]["name"]}\n\n')
                f.write("Завершённые задачи:\n")
                f.writelines(completed_tasks)
                f.write("\nОставшиеся задачи:\n")
                f.writelines(uncompleted_tasks)

        except IOError:
            print("An IOError has occurred!")


if __name__ == '__main__':
    generate_reports()
