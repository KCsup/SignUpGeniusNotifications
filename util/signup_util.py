from util import log_util as lutil
import datetime
import requests as r


class SignUp:
    def __init__(self, url, id, title, author):
        self.url = url
        self.id = id
        self.title = title
        self.author = author

        self.roles = []
        

    def to_json(self):
        roles_json_array = []
        for r in self.roles:
            roles_json_array.append(r.to_json())

        return {
                "url": self.url,
                "id": self.id,
                "title": self.title,
                "author": self.author,
                "roles": roles_json_array
            }

    def set_roles(self, roles):
        self.roles = roles


    def get_roles(self, days_out=None, days_from=0, hours_out=None, hours_from=0, include_full=True, include_ended=True):
        roles = self.roles

        if roles:
            if days_out:
                roles = [r for r in roles if r.get_days_until() <= days_out and \
                        r.get_days_until() >= days_from]
            elif hours_out:
                roles = [r for r in roles if r.get_hours_until() <= hours_out and \
                        r.get_hours_until() >= hours_from]

            if not include_full:
                roles = [r for r in roles if not r.full()]

            if not include_ended:
                roles = [r for r in roles if not r.has_ended()]

        return roles

    def get_signup_message(self,
                           days_out=None,
                           days_from=0,
                           hours_out=None,
                           hours_from=0,
                           include_full=True,
                           include_time_detail=False):
        if not days_out and not hours_out:
            return None
        
        message = ""

        roles = self.get_roles(days_out=days_out,
                               days_from=days_from,
                               hours_out=hours_out,
                               hours_from=hours_from,
                               include_full=include_full)

        full_roles_seperated = [r for r in roles if r.full()]
        roles = [r for r in roles if not r.full()]

        if roles or full_roles_seperated:
            message += "\n<hr>"
        else:
            return message
        
        when_string = ""
        if include_time_detail:
            if days_out:
                when_string = f" in the next {days_out if days_out > 1 else ''} day{'s'[:days_out^1]}"
            elif hours_out:
                when_string = f" in the next {hours_out if hours_out > 1 else ''} hour{'s'[:hours_out^1]}"

        if roles:
            whole_needed = 0
            not_full_update = []
            for r in roles:
                not_full_update.append("- " + r.get_notification_role_string())
                whole_needed += r.needed
            
            not_full_update_str = "\n".join(not_full_update)
            not_full_update_str = f"<blockquote>{not_full_update_str}</blockquote>"

            not_full_title = f"'{self.title}' has {whole_needed} slot{'s'[:whole_needed^1]}" + \
                    f" available{when_string}:"
            
            message += "\n" + not_full_title + not_full_update_str

        if full_roles_seperated:
            full_update = []
            for r in full_roles_seperated:
                full_update.append("- " + r.get_notification_role_string())
                
            full_update_str = "\n".join(full_update)
            full_update_str = f"<blockquote>{full_update_str}</blockquote>"

            full_title = f"'{self.title}' has {len(full_roles_seperated)}" + \
                    f" full volunteering role{'s'[:len(full_roles_seperated)^1]}{when_string}:"

            message += "\n" + full_title + full_update_str
        
        message += "\n" + f"Link: <a href={self.url}>{self.url}</a>" + "\n" 
        return message
        

class SignUpRole:
    def __init__(self, title, needed, date, start_time, end_time):
        self.title = title
        self.needed = needed
        self.date = date
        self.start_time = start_time
        self.end_time = end_time

    def to_json(self):
        return {
                "title": self.title,
                "needed_count": self.needed,
                "date_string": self.date,
                "start_time_string": self.start_time,
                "end_time_string": self.end_time
            }
    
    def full(self): return self.needed == 0

    def get_testing_role_string(self):
        return f"Title: {self.title}" + "\n" + \
            f"   Status: {self.needed}" + "\n" + \
            f"   Date: {self.date}" + "\n" + \
            f"   Time: {self.start_time} - {self.end_time}"
   
    def get_notification_role_string(self):      
        status_string = f"{self.needed} slot{'s'[:self.needed^1]} available"
        if self.full():
            status_string = f"Full slots"

        return f"{status_string} on {self.date}" + \
                f" from {self.start_time} to {self.end_time}"

    def get_time_object(self):
        return datetime.datetime.fromtimestamp(self.start_time)

    def get_end_time_object(self):
        return datetime.datetime.fromtimestamp(self.end_time)

    def get_hours(self):
        return (self.get_end_time_object() - self.get_time_object()).total_seconds() / 3600

    def has_ended(self):
        return datetime.datetime.now() > self.get_end_time_object()

    def get_hours_until(self):
        return ((self.get_time_object() - datetime.datetime.now()).total_seconds()) / 3600

    def get_days_until(self):
        return self.get_hours_until() / 24


BASE_SIGNUP_GENIUS_URL = "https://api.signupgenius.com/v2/k"

def fix_signupgenius_url(url):
    if "signupgenius.com" not in url:
        return None

    new_url = url.replace("://m.", "://www.").replace("/#!/showSignUp/", "/go/")
    if not new_url.endswith("#/"): new_url += "#/"
    return new_url


def get_current_signups(signup_genius_token, with_roles=True) -> [SignUp]:
    signups = []
    
    signups_request = r.get(
        f"{BASE_SIGNUP_GENIUS_URL}/signups/created/active/",
        {"user_key": signup_genius_token}
    )

    if signups_request.ok:
        signups_array = signups_request.json()["data"]
        for signup_json in signups_array:
            signup = SignUp(
                signup_json["signupurl"],
                signup_json["signupid"],
                signup_json["title"],
                signup_json["contactname"]
            )

            signups.append(signup)

    if with_roles:
        for signup in signups:
            signup.set_roles(get_signup_roles_available(signup_genius_token, signup.id))
    
    return signups

        
def get_signup_roles_available(signup_genius_token, signup_id) -> [SignUpRole]:
    roles = []

    roles_request = r.get(
        f"{BASE_SIGNUP_GENIUS_URL}/signups/report/available/{signup_id}",
        {"user_key": signup_genius_token}
    )

    if roles_request.ok:
        roles_array = roles_request.json()["data"]["signup"]
        for role_json in roles_array:
            roles.append(SignUpRole(
                role_json["item"],
                role_json["myqty"], # Gives the amount of people NEEDED
                role_json["startdate"], # All the times below can be '0' (same as None)
                role_json["starttime"],
                role_json["endtime"]
            ))

    return roles

