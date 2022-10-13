"""Generate the sql from metadata. """

import yaml
import os
from dim.models.dq_checks.not_null import NotNull
from dim.models.dq_checks.uniqueness import Uniqueness
from dim.models.dq_checks.custom_sql_metrics import CustomSqlMetrics
from dim.models.dq_checks.table_row_count import TableRowCount
from dim.slack import Slack


CONFIG_ROOT_PATH = "dim_checks"
TEST_CLASS_MAPPING = {"not_null": NotNull, "uniqueness": Uniqueness, "sql_metrics" : CustomSqlMetrics, "table_row_count" : TableRowCount}


def get_all_paths_yaml(name, config_root_path: str):
    result = []
    for root, dirs, files in os.walk(config_root_path):
        for file in files:
            if name in file:
                result.append(os.path.join(root, file))
    return result


def read_config(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def main():
    name = '.yml'
    for config_path in get_all_paths_yaml(name, CONFIG_ROOT_PATH):
        config = read_config(config_path=config_path)
    # TODO: validate config, correct keys + types --add a function
        project_id, dataset_id, table_id = config_path.split("/")[1:-1]
        for config in config["dim_config"]:
            dataset_owner = config["owner"]["email"]
            for test in config["tests"]:
                test_type = test["type"]
                dq_check = TEST_CLASS_MAPPING[test_type](
                    project_id=project_id,
                    dataset_id=dataset_id,
                    table_id=table_id,
                    config=test["config"],
                    dataset_owner=dataset_owner)
                # _, test_sql = dq_check.generate_test_sql()
                # dq_check.execute_test_sql(sql=test_sql)
                if test["config"]["slack_alert"].lower() == 'enabled':
                    slack_handles = config["owner"]["slack_handle"]
                    channel = test["config"]["channel"]
                    send_slack_alert(channel, slack_handles)

def send_slack_alert(channel, slack_handles):
    slack = Slack()
    df = slack.get_failed_dq_checks()
    slack.format_and_publish_slack_message(df, channel, slack_handles=slack_handles)


if __name__ == "__main__":
    main()