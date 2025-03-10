import json

from elasticsearch import Elasticsearch

client = Elasticsearch(
    "",
    api_key="",
)

index_name = "redlie_test_2"


def exist(filename):
    exists = client.exists(index=index_name, id=filename)
    return exists


def get_results(filename):
    document = client.get(index=index_name, id=filename)
    deserialize = json.loads(document["_source"]["class_data"])
    return deserialize


def send_results(filename, results):
    response = {
        "all_records": results["all_records"],
        "ci_words2": results["ci_words2"],
        "disp": results["disp"],
        "disp1": results["disp1"],
        "disp2": results["disp2"],
        "disp3": results["disp3"]
    }
    serialize = json.dumps(response)
    client.index(index=index_name, id=filename, body={"class_data": serialize})
    print(f"sent to elastic: {serialize}")
