YOU NEED TO DO THIS FROM YOUR COMPUTER.


# 📅 Canvas to Calendar Bot (Smart Edition)

This tool automatically pulls your Assignments, Announcements, and Events from Canvas and syncs them to your Google/Apple Calendar. 

**✨ New Features:**
* **Auto-Sync:** Updates every day at 5:00 AM.
* **Smart Parsing:** If a professor posts "Quiz on the 28th" in an announcement, this bot moves it to the correct date automatically.
* **"Next Class" Logic:** If an announcement says "Quiz next class," the bot checks your personal timetable and figures out the exact date.

## 🚀 How to set this up for yourself

### Step 1: Get the Code
1. Click the **Fork** button (top right of this page) to copy this repository to your own account.

### Step 2: Get Your Canvas Key
1. Log in to Canvas.
2. Go to **Account** → **Settings**.
3. Scroll down to **Approved Integrations** and click **+ New Access Token**.
4. Name it "Calendar" and copy the long code it gives you. (DO NOT FORGET THIS TOKEN)
5. this token is only available for four months so add a date four months in advance


### Step 3: Add Your Secrets (The Important Part)
1. Go to your new repository's **Settings** tab.
2. Click **Secrets and variables** → **Actions** → **New repository secret**.
3. You need to add these **3 Secrets**:

| Name | Value |
| :--- | :--- |
| `CANVAS_API_KEY` | Paste the long token you just copied. |
| `CANVAS_API_URL` | Paste our school's Canvas URL (e.g., `https://canvas.instructure.com`). *Must start with https://* |
| `MY_TIMETABLE` | (Optional) Your class schedule. See the code block below. |

PLEASE KEEP THE NAMING CONVENTION THE SAME

#### 📝 How to format `MY_TIMETABLE`
Copy the code below and change the days to match your schedule.
* **0** = Monday, **1** = Tuesday, **2** = Wednesday, **3** = Thursday, **4** = Friday, **5** = Saturday
* **Format:** `"Course Code": [Day numbers]`

```json
{
  "CS 363": [1, 3],
  "MATH 205": [0, 2, 4],
  "CS 101": [0, 2]
}
```
Step 4: Turn on the Robot
Go to the Actions tab.

Click Daily Calendar Sync on the left.

Click Enable Workflow (if asked).

Click Run workflow to start it for the first time.

Step 5: Get Your Link
Once the run turns Green ✅, go to Settings → Pages.

Under Branch, select main and click Save.

Your calendar link will appear at the top!

It will look like: https://(your-username).github.io/canvas-calendar/my_schedule.ics

Step 6: Add to Phone
iPhone: Settings → Apps → Calendar → Calendar Accounts → Add Account → Other → Add Subscribed Calendar.

Google: Calendar Website → "+" next to Other Calendars → From URL.
