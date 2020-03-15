import json
import os
import unittest
import datetime as dt

import requests

import tasks


class TestMedrating(unittest.TestCase):

    def setUp(self):
        self.users_json = tasks.get_data(tasks.API_USERS)
        self.todos_json = tasks.get_data(tasks.API_TODOS)
        self.completed_all, self.uncompleted_all = (
            tasks.make_report_for_all_users(self.todos_json)
            )
        self.task = self.todos_json[1]
        self.user_id = self.task['userId']
        self.user = self.users_json[1]
        self.completed_user_tasks = self.completed_all.get(self.user_id, [])
        self.uncompleted_user_tasks = (
            self.uncompleted_all.get(self.user_id, [])
            )

    def test_get_json(self):
        self.assertRaises(
            json.decoder.JSONDecodeError,
            tasks.get_data,
            tasks.API_BASE
            )

        self.assertRaises(
            requests.exceptions.HTTPError,
            tasks.get_data,
            "http://example.com/api/123"
            )

        self.assertRaises(
            requests.exceptions.ConnectionError,
            tasks.get_data,
            f"http://invalid-url-test/wrong_page"
            )

        self.assertIsInstance(self.users_json, list)
        self.assertIsInstance(self.users_json[0], dict)

    def test_report_all_users(self):
        sample_task = self.task['title']

        self.assertTrue(
            (sample_task in self.completed_user_tasks) ^
            (sample_task in self.uncompleted_user_tasks)
            )

    def test_formatting(self):
        output = tasks.format_report(
            self.user,
            self.completed_all.get(self.user_id),
            self.uncompleted_all.get(self.user_id)
        )

        user_info_string = output.split('\n')[0]
        completed_task_string = output.split('\n')[4]
        self.assertEqual(
            user_info_string.split()[-3],
            f"<{self.user['email']}>")
        # Year
        self.assertEqual(
            user_info_string.split()[-2],
            dt.datetime.now().date().strftime("%d.%m.%Y")
            )
        # Task from list of tasks
        self.assertEqual(
            completed_task_string,
            self.completed_user_tasks[0]
            )

    def test_save_to_file(self):
        self.assertIsNone(tasks.save_report_to_file(self.user, [], []))
        self.assertRaises(
            FileNotFoundError,
            tasks.save_report_to_file,
            self.user,
            self.completed_user_tasks,
            self.uncompleted_user_tasks
            )

if __name__ == '__main__':
    unittest.main()
