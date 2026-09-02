from pystro.config import Config
from pystro.apis.api import get_plan_jobs
from pystro.helpers.oql import OQLQuery, field
from datetime import timedelta, datetime, timezone

def main():
    config = Config.from_json()
    d = (datetime.now(timezone.utc) - timedelta(weeks=2)).date()
    two_weeks_ago = f"{d.isoformat()}T00:00:00.000Z"

    q = (field('jobruns.compositeStatus.status').not_in(['SUCC','CANCL'])) & (field('schedTime') <= two_weeks_ago)
    query = OQLQuery(q)

    plan_jobs = get_plan_jobs(config, oql = query)
    for plan_job in plan_jobs:
        print(plan_job)

if __name__ == "__main__":
    main()