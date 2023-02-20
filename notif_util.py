import signup_util as sutil
import canvas_util as cutil
import google_calendar_util as gcalutil
from datetime import date, timedelta


def get_notification_message(days_out, include_when=False):
    notif_message = ""
    signups_notify = get_signups_to_notify(days_out)
    for signup in signups_notify:
        roles = signup.get_roles_to_notify(days_out)

        whole_count = 0
        signup_string = ""

        when_string = f" in the next {days_out} days"
        if not include_when:
            when_string = ""
        elif days_out == 0:
            when_string = " today"
        elif days_out == 1:
            when_string = " tomorrow"
        

        for r in roles:
            signup_string += "\n" + f"   {r.get_notification_role_string()}"
            whole_count += r.get_needed_count()

        signup_string += "\n" + f"   Link: <a href={signup.url}>{signup.url}</a>"

        signup_string = f"'{signup.title}' has {whole_count} volunteering" + \
                f" slot{'s'[:whole_count^1]} available{when_string}:" + \
                signup_string

        if notif_message: notif_message += "\n\n"

        notif_message += signup_string

    notif_message = notif_message.replace("\n", "<br>")

    return notif_message, len(signups_notify)


def get_notification_message_hourly(hours_out, include_when=False):
    notif_message = ""
    signups_notify = get_signups_to_notify_hourly(hours_out)
    for signup in signups_notify:
        roles = signup.get_roles_to_notify_hourly(hours_out)

        whole_count = 0
        signup_string = ""

        when_string = f" in the next {hours_out} hour{'s'[:hours_out^1]}"
        if not include_when:
            when_string = ""

        for r in roles:
            signup_string += "\n" + f"   {r.get_notification_role_string()}"
            whole_count += r.get_needed_count()

        signup_string += "\n" + f"   Link: <a href={signup.url}>{signup.url}</a>"

        signup_string = f"'{signup.title}' has {whole_count} volunteering" + \
                f" slot{'s'[:whole_count^1]} available{when_string}:" + \
                signup_string

        if notif_message: notif_message += "\n\n"

        notif_message += signup_string

    notif_message = notif_message.replace("\n", "<br>")

    return notif_message, len(signups_notify)


def get_signups_to_notify(days_out):
    signups = []
    events = gcalutil.get_nhs_events()
    for e in events:
        signup_data = get_signup_from_event(e, 5)

        if signup_data == None: continue

        signup, url = signup_data[0], signup_data[1]

        roles = signup.get_roles_to_notify(days_out)

        if not roles: continue

        signups.append(signup)

    return signups


def get_signups_to_notify_hourly(hours_out):
    signups = []
    events = gcalutil.get_nhs_events()
    for e in events:
        signup_data = get_signup_from_event(e, 5)

        if signup_data == None: continue

        signup, url = signup_data[0], signup_data[1]

        roles = signup.get_roles_to_notify_hourly(hours_out)

        if not roles: continue

        signups.append(signup)

    return signups



def send_weekly_notification():
    notif_message, signup_count = get_notification_message(7)

    if signup_count == 0:
        print("No signups for weekly update, skipping.")
        return

    current_date_str = date.today().strftime("%m/%d/%Y")
    notif_title = f"Weekly Update for SignUps ({current_date_str})"
    notif_message = notif_title + "<br><br>" + notif_message
    default_course = cutil.get_notification_course_id()
    cutil.send_announcement(default_course, notif_title, notif_message)


def send_hourly_notification(hours_out, include_when=False):
    notif_message, signup_count = get_notification_message_hourly(hours_out, include_when)

    if signup_count == 0:
        print(f"No signups for hourly update ({hours_out} hours), skipping.")
        return

    current_date_str = date.today().strftime("%m/%d/%Y")
    notif_title = f"Hourly Update for SignUps ({current_date_str})"
    notif_message = notif_title + "<br><br>" + notif_message
    default_course = cutil.get_notification_course_id()
    cutil.send_announcement(default_course, notif_title, notif_message)



def get_signup_from_event(cal_event, retries):
    desc = gcalutil.get_raw_description(cal_event).split(" ")
    for i in desc:
        url = sutil.fix_signupgenius_url(i)

        if url == None: continue

        return sutil.get_signup_data(url, retries), url
    
    return None
