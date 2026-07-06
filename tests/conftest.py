import os
import pytest
import logging

import astrodb_utils
from astrodb_utils import build_db_from_json

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def db():
    logger.info(f"Using version {astrodb_utils.__version__} of astrodb_utils")

    db = build_db_from_json()

    assert os.path.exists(
        "all_streams_unique_v3.sqlite"
    ), "Database file 'all_streams_unique_v3.sqlite' was not created."

    logger.info(
        "Loaded all_streams_unique_v3 database using build_db_from_json in conftest.py"
    )

    return db
