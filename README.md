# SignUpGeniusNotifications
A connection between SignupGenius and Canvas LMS to send updates to a certain course. 

## Deprecated
This repo will no longer receive updates for this project. New changes will be made on the DHS's NHS GitHub Organization at the following URL:
https://github.com/DHS-National-Honor-Society/SignUpGeniusNotifications

## Config Template
```json
{
  "canvas_token": "str; Canvas LMS Token here",
  "default_canvas_course": "int; The Canvas Course ID for the announcements to be sent",
  "signup_genius_token": "str; SignUpGenius Token here",
  "daily_time": "str; Time time for the daily updates, in the format '%H:%M' (ex. 07:00, 13:30)",
  "hourly_minute": "str; Minute marker for the hourly updates, in the format ':%M' (ex. :05, :15)",
  "weekly_update_day": "str; The day of the week that the weekly update will send on, in the format '%A' (ex. Monday, Tuesday, ...)",
  "request_retries": "int; The amount of retry attempts for the SG API calls",
  "contacts": "[[str]]; The contacts for the notification string, formatted [['NAME', 'EMAIL'], ...]",
  "google_calendar_id": "str; The Calendar ID of the Google Calendar to be updated"
}
```
