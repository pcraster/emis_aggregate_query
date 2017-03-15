import os
from emis_aggregate_query import create_app

os.environ["EMIS_CONFIGURATION"] = \
    os.environ.get("EMIS_CONFIGURATION") or "production"
app = create_app(os.getenv("EMIS_CONFIGURATION"))
