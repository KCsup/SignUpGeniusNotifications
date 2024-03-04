from util import notif_util as nutil, \
    log_util as lutil, canvas_util as cutil, \
    config_util, signup_util as sutil, \
    google_calendar_util as gcutil
import schedule
import time
import traceback
import json
import datetime

current_signups = []


def hourly_job():
    lutil.log("Starting hourly job...")
    
    conf = config_util.get_config()

    current_signups = sutil.get_current_signups(conf["signup_genius_token"])
    job_signups = sutil.get_filtered_signups(current_signups,
                                             hours_out=2,
                                             hours_from=1,
                                             include_full=False,
                                             include_ended=False)
    
    nutil.send_notification(job_signups,
                            conf["default_canvas_course"],
                            hours_out=2,
                            hours_from=1,
                            include_full=False,
                            include_when=True)

    gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Hourly job done.")


def daily_job():
    lutil.log("Starting daily job...")
    
    conf = config_util.get_config()

    now = datetime.datetime.now()

    if now.strftime("%A") == conf["weekly_update_day"]:
        lutil.log("Moving to weekly job...")
        weekly_job()
        return

    current_signups = sutil.get_current_signups(conf["signup_genius_token"])
    job_signups = sutil.get_filtered_signups(current_signups,
                                             days_out=1,
                                             include_full=False,
                                             include_ended=False)
    
    nutil.send_notification(job_signups,
                            conf["default_canvas_course"],
                            days_out=1,
                            include_full=False,
                            include_when=True)

    gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Daily job done.")


def weekly_job():
    lutil.log("Starting weekly job...")
    
    conf = config_util.get_config()

    current_signups = sutil.get_current_signups(conf["signup_genius_token"])
    job_signups = sutil.get_filtered_signups(current_signups,
                                             days_out=7,
                                             include_full=False,
                                             include_ended=False)
    
    nutil.send_weekly_notification(job_signups,
                                   conf["default_canvas_course"],
                                   include_full=False,
                                   include_when=False) # No need to say "in the next 7 days"

    gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Weekly job done.")



def main():
    lutil.log("Starting script...")

    daily_time = config_util.get_config_item("daily_time")
    hourly_minute = config_util.get_config_item("hourly_minute")

    # schedule.every().hour.at(hourly_minute).do(hourly_job)

    schedule.every().day.at(daily_time).do(daily_job)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        lutil.log("Exception Thrown:")
        traceback.print_exc()
        
    lutil.handle_logger_close()


    
