import os
import re
import json
from canvasapi import Canvas
from ics import Calendar, Event
from datetime import datetime, timedelta

# --- LOAD CONFIGURATION ---
def load_config():
    timetable_str = os.environ.get("MY_TIMETABLE", "{}")
    try:
        return json.loads(timetable_str)
    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse MY_TIMETABLE.")
        return {}

CONFIG = load_config()
COURSE_CONFIGS = CONFIG.get("courses", {})

def get_course_config(course_name):
    """ Matches "CS-363-Spring" to config key "CS 363" """
    for key, data in COURSE_CONFIGS.items():
        clean_key = key.replace(" ", "").upper()
        clean_name = course_name.replace(" ", "").upper()
        if clean_key in clean_name:
            return data
    return None

def is_relevant_announcement(title, message, my_sections):
    """
    The Bouncer Logic 🛡️:
    Only runs if you have specific sections defined.
    """
    text = (title + " " + message).upper()
    mentioned_sections = set(re.findall(r"\b[LSR]\d+\b", text))
    
    if not mentioned_sections:
        return True 

    for sec in my_sections:
        if sec.upper() in mentioned_sections:
            return True
            
    print(f"   🚫 Skipping: Targeted at {mentioned_sections}, but you are {my_sections}")
    return False

def get_next_class_date(class_days, posted_date_obj):
    if not class_days: return None
    posted_day_idx = posted_date_obj.weekday()
    class_days = sorted(class_days)
    days_ahead = 0
    for day in class_days:
        if day > posted_day_idx:
            days_ahead = day - posted_day_idx
            break
    if days_ahead == 0:
        days_ahead = (7 - posted_day_idx) + class_days[0]
    return posted_date_obj + timedelta(days=days_ahead)

def find_date_in_text(text, default_date_str, class_days):
    if not text: return datetime.strptime(default_date_str, "%Y-%m-%d")
    posted_date_obj = datetime.strptime(default_date_str[:10], "%Y-%m-%d")
    current_year = datetime.now().year

    # 1. Next Class Logic
    if re.search(r"\b(next\s+class|next\s+lecture)\b", text, re.IGNORECASE):
        next_date = get_next_class_date(class_days, posted_date_obj)
        if next_date:
            print(f"   ✨ Found 'Next Class' -> Moved to {next_date.date()}")
            return next_date

    # 2. Date Parsing
    pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})"
    match = re.search(pattern, text, re.IGNORECASE)
    try:
        if match:
            month_str, day = match.group(1), int(match.group(2))
            months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
            month = months[month_str.lower()[:3]]
            year = current_year
            if month < posted_date_obj.month and (posted_date_obj.month - month) > 6:
                year += 1 
            return datetime(year, month, day)
    except:
        pass
    return posted_date_obj

def main():
    API_URL = os.environ.get("CANVAS_API_URL")
    API_KEY = os.environ.get("CANVAS_API_KEY")
    
    if not API_URL or not API_KEY:
        print("❌ Error: Missing CANVAS_API_URL or CANVAS_API_KEY")
        return

    canvas = Canvas(API_URL, API_KEY)
    cal = Calendar()
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print("🔄 Syncing...")
    courses = canvas.get_courses(enrollment_state='active')
    
    for course in courses:
        config_data = get_course_config(course.course_code)
        
        # If my_sections is empty [], it means "Take Everything" (Like Math 205)
        class_days = config_data['days'] if config_data else []
        my_sections = config_data['sections'] if config_data else []
        
        print(f"📂 Scanning {course.course_code} (Sections: {my_sections if my_sections else 'ALL'})")

        try:
            # 1. Assignments
            for assign in course.get_assignments(bucket='upcoming'):
                if assign.due_at:
                    e = Event()
                    e.name = f"📝 {assign.name} ({course.course_code})"
                    e.begin = assign.due_at
                    e.description = assign.html_url
                    cal.events.add(e)
            
            # 2. Announcements
            for ann in course.get_discussion_topics(only_announcements=True):
                if ann.posted_at and ann.posted_at > start_date:
                    
                    # FILTER: Only run logic IF we have specific sections defined
                    if my_sections and not is_relevant_announcement(ann.title, ann.message, my_sections):
                        continue 

                    e = Event()
                    full_text = f"{ann.title} {ann.message}"
                    parsed_date = find_date_in_text(full_text, ann.posted_at, class_days)
                    
                    e.name = f"📢 {ann.title} ({course.course_code})"
                    e.begin = parsed_date
                    e.make_all_day()
                    e.description = f"Originally Posted: {ann.posted_at[:10]}\n{ann.html_url}\n\n{ann.message[:200]}..."
                    cal.events.add(e)

        except Exception as e:
            pass

    with open('my_schedule.ics', 'w', encoding='utf-8') as f:
        f.writelines(cal)
    
    print("✅ Success! Calendar updated.")

if __name__ == "__main__":
    main()
