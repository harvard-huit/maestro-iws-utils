import argparse

from pystro.config import Config
from pystro.api import get_plan_jobs
from pystro.oql import OQLQuery, field
from datetime import timedelta, datetime, timezone

def main():
    parser = argparse.ArgumentParser(description='Retrieve the master engine from the Maestro API')
    parser.add_argument('-e', '--environment', help='The environment to use from the configuration file', default='test')
    parser.add_argument('-n', '--num_days', type=int, help='The number of days to look back for old jobs', default=14)
    args = parser.parse_args()

    config = Config.from_json(environment=args.environment)
    num_days = args.num_days
    d = (datetime.now(timezone.utc) - timedelta(days=num_days)).date()
    cutoff_date = f"{d.isoformat()}T00:00:00.000Z"

    q = (field('jobruns.compositeStatus.status').not_in(['SUCC','CANCL'])) & (field('schedTime') <= cutoff_date)
    query = OQLQuery(q)

    plan_jobs = get_plan_jobs(config, oql = query)
    for plan_job in plan_jobs:
        print(plan_job)
        for action in plan_job.actions:
            print(f" {action}")

if __name__ == "__main__":
    main()