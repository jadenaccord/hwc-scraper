from apscheduler.schedulers.blocking import BlockingScheduler
from __main__ import __main__

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=8)
def scheduled_job():
    print('Running scheduled job.')


sched.start()
