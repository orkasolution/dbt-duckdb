import pytest
from pathlib import Path
import pandas as pd
import tempfile

from dbt.tests.util import (
    check_relations_equal,
    run_dbt,
)
from deltalake.writer import write_deltalake

delta_schema_yml = """
version: 2
sources:
  - name: delta_source
    meta:
      plugin: delta
    tables:
      - name: table_1
        description: "An delta table"
        meta:
          delta_table_path: "/workspaces/dbt-duckdb/lineitem"

"""

delta1_sql = """
    {{ config(materialized='table') }}
    select * from {{ source('delta_source', 'table_1') }} limit 200
"""


@pytest.mark.skip_profile("buenavista", "md")
class TestPlugins:
    @pytest.fixture(scope="class")
    def delta_test_table1(self):
        td = tempfile.TemporaryDirectory() 
        path = Path(td.name)
        table_path = path / "test_delta_table1"

        df = pd.DataFrame({"x": [1, 2, 3]})
        write_deltalake(table_path, df, mode="overwrite")

        yield table_path

        td.cleanup()

    @pytest.fixture(scope="class")
    def profiles_config_update(self, dbt_profile_target):
        plugins = [{"module": "delta"}]
        return {
            "test": {
                "outputs": {
                    "dev": {
                        "type": "duckdb",
                        "path": dbt_profile_target.get("path", ":memory:"),
                        "plugins": plugins,
                    }
                },
                "target": "dev",
            }
        }

    @pytest.fixture(scope="class")
    def models(self, delta_test_table1):
        return {
            "source_schema.yml": delta_schema_yml.format(
                test_delta_path1=delta_test_table1
            ),
            "delta_table1.sql": delta1_sql,
        }

    def test_plugins(self, project):
        results = run_dbt()
        #assert len(results) == 4

        # check_relations_equal(
        #     project.adapter,
        #     [
        #         "delta_table3",
        #         "delta_table3_expected",
        #     ],
        # )
        # res = project.run_sql("SELECT count(1) FROM 'delta_table3'", fetch="one")
        # assert res[0] == 2
