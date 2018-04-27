from crontab import CronTab


cron  = CronTab(user=True)


cron.remove_all(comment='water_timer')
cron.write()



cron  = CronTab(user=True)

job = cron.new(command='sudo python3 /home/pi/notification1.py',comment='water_timer')
job.hour.on(2)
job.minute.on(0)
cron.write()






