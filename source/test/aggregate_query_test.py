import os.path
import unittest
import uuid
from flask import current_app, json
from emis_aggregate_query import create_app, db
from emis_aggregate_query.api.schema import *


class AggregateQueryTestCase(unittest.TestCase):


    def setUp(self):
        self.app = create_app("test")
        self.app.config["TESTING"] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        self.user1 = uuid.uuid4()
        self.user2 = uuid.uuid4()
        self.user3 = uuid.uuid4()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def post_aggregate_queries(self):

        # user1: two queries
        # user2: one query
        # user3: no query
        payloads = [
                {
                    "user": self.user1,
                    "model": {"meh1": "mah1"}
                },
                {
                    "user": self.user2,
                    "model": {"meh2": "mah2"}
                },
                {
                    "user": self.user1,
                    "model": {"meh3": "mah3"}
                },
            ]

        for payload in payloads:
            response = self.client.post("/aggregate_queries",
                data=json.dumps({"aggregate_query": payload}),
                content_type="application/json")
            data = response.data.decode("utf8")

            self.assertEqual(response.status_code, 201, "{}: {}".format(
                response.status_code, data))

    def do_test_get_aggregate_queries_by_user(self,
            user_id,
            nr_results_required):

        self.post_aggregate_queries()

        response = self.client.get("/aggregate_queries/{}".format(user_id))
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_queries" in data)

        queries = data["aggregate_queries"]

        self.assertEqual(len(queries), nr_results_required)


    def test_get_aggregate_queries_by_user1(self):
        self.do_test_get_aggregate_queries_by_user(self.user1, 2)


    def test_get_aggregate_queries_by_user2(self):
        self.do_test_get_aggregate_queries_by_user(self.user2, 1)


    def test_get_aggregate_queries_by_user3(self):
        self.do_test_get_aggregate_queries_by_user(self.user3, 0)


    def test_get_all_aggregate_queries1(self):
        # No queries posted.
        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_queries" in data)
        self.assertEqual(data["aggregate_queries"], [])


    def test_get_all_aggregate_queries2(self):
        # Some queries posted.
        self.post_aggregate_queries()

        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_queries" in data)

        queries = data["aggregate_queries"]

        self.assertEqual(len(queries), 3)


    def test_get_aggregate_query(self):
        self.post_aggregate_queries()

        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")
        data = json.loads(data)
        queries = data["aggregate_queries"]
        query = queries[0]
        uri = query["_links"]["self"]
        response = self.client.get(uri)

        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_query" in data)

        self.assertEqual(data["aggregate_query"], query)

        self.assertTrue("id" in query)
        self.assertTrue("user" in query)
        self.assertTrue("posted_at" in query)
        self.assertTrue("patched_at" in query)

        self.assertTrue("model" in query)
        self.assertEqual(query["model"], {"meh1": "mah1"})

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "draft")

        self.assertTrue("_links" in query)

        links = query["_links"]

        self.assertTrue("self" in links)
        self.assertEqual(links["self"], uri)

        self.assertTrue("collection" in links)


    def test_get_unexisting_aggregate_query(self):
        self.post_aggregate_queries()

        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")
        data = json.loads(data)
        queries = data["aggregate_queries"]
        query = queries[0]
        uri = query["_links"]["self"]
        # Invalidate uri
        uri = os.path.join(os.path.split(uri)[0], str(uuid.uuid4()))
        response = self.client.get(uri)

        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 400, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_post_empty_aggregate_query(self):
        payload = {
                "user": uuid.uuid4(),
                "model": {"meh": "mah"}
            }
        response = self.client.post("/aggregate_queries",
            data=json.dumps({"aggregate_query": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 201, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_query" in data)

        query = data["aggregate_query"]

        self.assertTrue("id" in query)
        self.assertTrue("user" in query)
        self.assertTrue("posted_at" in query)
        self.assertTrue("patched_at" in query)

        self.assertTrue("model" in query)
        self.assertEqual(query["model"], {"meh": "mah"})

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "draft")

        self.assertTrue("_links" in query)

        links = query["_links"]

        self.assertTrue("self" in links)
        self.assertTrue("collection" in links)


    def test_post_aggregate_query(self):
        user_id = uuid.uuid4()
        payload = {
                "user": user_id,
                "model": {"meh": "mah"}
            }
        response = self.client.post("/aggregate_queries",
            data=json.dumps({"aggregate_query": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 201, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_query" in data)

        query = data["aggregate_query"]

        self.assertTrue("id" in query)
        self.assertTrue("user" in query)
        self.assertTrue("posted_at" in query)
        self.assertTrue("patched_at" in query)

        self.assertTrue("model" in query)
        self.assertEqual(query["model"], {"meh": "mah"})

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "draft")

        self.assertTrue("_links" in query)

        links = query["_links"]

        self.assertTrue("self" in links)
        self.assertTrue("collection" in links)

        self.do_test_get_aggregate_queries_by_user(user_id, 1)


    def test_post_bad_request(self):
        response = self.client.post("/aggregate_queries")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 400, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_post_unprocessable_entity(self):
        payload = ""
        response = self.client.post("/aggregate_queries",
            data=json.dumps({"aggregate_query": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 422, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("message" in data)


    def test_patch_edit_status(self):
        user_id = uuid.uuid4()
        payload = {
                "user": user_id,
                "model": {"meh": "mah"}
            }
        response = self.client.post("/aggregate_queries",
            data=json.dumps({"aggregate_query": payload}),
            content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 201, "{}: {}".format(
            response.status_code, data))

        query = json.loads(data)["aggregate_query"]
        query_id = query["id"]

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "draft")

        self.assertTrue("execute_status" in query)
        self.assertEqual(query["execute_status"], "pending")

        payload = {
            "edit_status": "final"
        }

        uri = query["_links"]["self"]
        response = self.client.patch(uri,
            data=json.dumps(payload), content_type="application/json")
        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        query = json.loads(data)["aggregate_query"]

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "final")

        self.assertEqual(query["id"], query_id)
        self.assertEqual(query["user"], str(user_id))


    def test_delete_aggregate_query(self):
        self.post_aggregate_queries()

        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")
        data = json.loads(data)
        queries = data["aggregate_queries"]
        query = queries[0]
        uri = query["_links"]["self"]
        response = self.client.delete(uri)

        data = response.data.decode("utf8")

        self.assertEqual(response.status_code, 200, "{}: {}".format(
            response.status_code, data))

        data = json.loads(data)

        self.assertTrue("aggregate_query" in data)

        self.assertEqual(data["aggregate_query"], query)

        self.assertTrue("id" in query)
        self.assertTrue("user" in query)
        self.assertTrue("posted_at" in query)
        self.assertTrue("patched_at" in query)

        self.assertTrue("model" in query)
        self.assertEqual(query["model"], {"meh1": "mah1"})

        self.assertTrue("edit_status" in query)
        self.assertEqual(query["edit_status"], "draft")

        self.assertTrue("_links" in query)

        links = query["_links"]

        self.assertTrue("self" in links)
        self.assertEqual(links["self"], uri)

        self.assertTrue("collection" in links)


        response = self.client.get("/aggregate_queries")
        data = response.data.decode("utf8")
        data = json.loads(data)
        queries = data["aggregate_queries"]
        self.assertEqual(len(queries), 2)


if __name__ == "__main__":
    unittest.main()
