import os
os.environ["AGGREGATE_QUERY_CONFIGURATION"] = "development"
from server import app


app.run(host="0.0.0.0")
