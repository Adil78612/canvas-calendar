import os
from canvasapi import Canvas
from ics import Calendar, Event
from datetime import datetime, timedelta

def main():
    # 1. Setup Canvas API
    API_URL = os.environ["CANVAS_API_URL"]
    API_KEY = os.environ["CANVAS_API_KEY"]
    canvas = Canvas(API_URL, API_KEY)
    
    # 2. Create a new Calendar
    cal = Calendar()
    
    # 3. Calculate Date Range (Past 30 days to Next 365 days)
    #    We check the past to catch announcements posted recently.
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    print("🔄 Syncing Assignments, Events, and Announcements...")

    # --- GET ASSIGNMENTS & ANNOUNCEMENTS (Course by Course) ---
    courses = canvas.get_courses(enrollment_state='active')
    
    for course in courses:
        try:
            # A. Get Assignments
            assignments = course.get_assignments(bucket='upcoming')
            for assign in assignments:
                if assign.due_at:
                    e = Event()
                    e.name = f"📝 {assign.name} ({course.course_code})"
                    e.begin = assign.due_at
                    e.description = assign.html_url
                    cal.events.add(e)
            
            # B. Get Announcements (Last 14 days only, to keep calendar clean)
            #    Note: Announcements don't have a "due date", so we use the "posted_at" date.
            announcements = course.get_discussion_topics(only_announcements=True)
            for ann in announcements:
                # Simple check: Is it recent?
                if ann.posted_at and ann.posted_at > start_date:
                    e = Event()
                    e.name = f"📢 {ann.title} ({course.course_code})"
                    e.begin = ann.posted_at
                    e.make_all_day() # Make it an all-day banner so you see it
                    e.description = f"Read more: {ann.html_url}\n\n{ann.message[:200]}..."
                    cal.events.add(e)

        except Exception as e:
            print(f"⚠️ Skipped {course.name} (Access Denied)")

    # --- GET CALENDAR EVENTS (Global Reminders) ---
    # This catches "Quiz on 28th" if the prof put it on the calendar but not as an assignment.
    try:
        user = canvas.get_current_user()
        events = user.get_calendar_events(start_date=start_date, end_date=end_date)
        for event in events:
            e = Event()
            e.name = f"🗓️ {event.title}"
            e.begin = event.start_at
            # Some events don't have an end time, so we default to +1 hour
            if event.end_at:
                e.end = event.end_at
            else:
                e.duration = {"hours": 1}
            e.description = event.description or ""
            cal.events.add(e)
            
    except Exception as e:
        print(f"⚠️ Could not fetch generic calendar events: {e}")

    # 4. Save the file
    with open('my_schedule.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal)
    
    print("✅ Success! Calendar file updated.")

if __name__ == "__main__":
    main()
