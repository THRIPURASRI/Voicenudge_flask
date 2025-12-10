import csv
import random

OUTPUT_PATH = "train/priority_dataset_1000.csv"

CATEGORIES = ["Work", "Study", "Personal", "Health", "Errands", "Finance"]
PRIORITIES = ["High", "Medium", "Low"]

# Time phrases
TIME_PHRASES = [
    "today at 8:00 pm",
    "today at 9:30 pm",
    "tonight at 10:00 pm",
    "tomorrow at 6:30 am",
    "tomorrow at 7:00 pm",
    "tomorrow morning at 7:30 am",
    "tomorrow evening at 8:00 pm",
    "this weekend at 5:00 pm",
    "on Friday at 7:30 pm",
    "on Saturday at 4:00 pm",
    "on Sunday at 6:00 pm",
    "next Monday at 9:00 am",
    "next Tuesday at 3:00 pm",
    "next Wednesday at 5:30 pm",
    "next Thursday at 11:00 am",
    "before midnight today",
    "before lunch at 1:00 pm",
    "after lunch at 2:30 pm",
    "after dinner at 9:30 pm",
]

# Templates keyed by (category, priority)
TEMPLATES = {
    ("Work", "High"): [
        "Finish critical project report {time}",
        "Prepare client presentation urgently {time}",
        "Fix production bug immediately {time}",
        "Submit deployment plan before deadline {time}",
        "Complete sprint tasks ASAP {time}",
    ],
    ("Work", "Medium"): [
        "Review pull requests {time}",
        "Refactor old code module {time}",
        "Update project documentation {time}",
        "Plan tasks for next sprint {time}",
        "Review design mockups {time}",
    ],
    ("Work", "Low"): [
        "Clean up old branches in git {time}",
        "Organize project folders {time}",
        "Review optional tech article {time}",
        "Experiment with new library {time}",
        "Review long-term backlog items {time}",
    ],

    ("Study", "High"): [
        "Revise important exam chapters {time}",
        "Solve previous year question papers {time}",
        "Prepare notes for tomorrow's test {time}",
        "Finish assignment due soon {time}",
        "Practice coding problems urgently {time}",
    ],
    ("Study", "Medium"): [
        "Watch recorded lecture {time}",
        "Summarize class notes {time}",
        "Practice a few coding problems {time}",
        "Read textbook chapter calmly {time}",
        "Plan study schedule for the week {time}",
    ],
    ("Study", "Low"): [
        "Browse optional reference materials {time}",
        "Skim through extra readings {time}",
        "Review solved examples casually {time}",
        "Explore new online course {time}",
        "Read tech blog article {time}",
    ],

    ("Personal", "High"): [
        "Call parents urgently {time}",
        "Attend important family call {time}",
        "Handle personal emergency task {time}",
        "Complete critical personal work {time}",
        "Talk to close friend about urgent issue {time}",
    ],
    ("Personal", "Medium"): [
        "Catch up with friend on call {time}",
        "Plan weekend outing {time}",
        "Journal about the day {time}",
        "Organize wardrobe {time}",
        "Clean room properly {time}",
    ],
    ("Personal", "Low"): [
        "Read a novel chapter {time}",
        "Watch a relaxing movie {time}",
        "Scroll social media freely {time}",
        "Listen to music {time}",
        "Browse memes for fun {time}",
    ],

    ("Health", "High"): [
        "Visit doctor immediately {time}",
        "Take important medication {time}",
        "Schedule emergency health checkup {time}",
        "Handle severe health issue {time}",
        "Monitor high fever closely {time}",
    ],
    ("Health", "Medium"): [
        "Go for evening walk {time}",
        "Do home workout {time}",
        "Practice yoga session {time}",
        "Prepare healthy meal {time}",
        "Track calories after dinner {time}",
    ],
    ("Health", "Low"): [
        "Do light stretching {time}",
        "Watch fitness video {time}",
        "Read health tips article {time}",
        "Plan diet chart someday {time}",
        "Research new workout ideas {time}",
    ],

    ("Errands", "High"): [
        "Pay electricity bill before cut off {time}",
        "Recharge mobile plan before expiry {time}",
        "Submit important form {time}",
        "Pick up urgent courier {time}",
        "Refill gas cylinder soon {time}",
    ],
    ("Errands", "Medium"): [
        "Buy groceries {time}",
        "Collect laundry {time}",
        "Visit ATM to withdraw cash {time}",
        "Drop parcel at post office {time}",
        "Get bike serviced {time}",
    ],
    ("Errands", "Low"): [
        "Window shop at mall {time}",
        "Browse items online {time}",
        "Check out new store nearby {time}",
        "Look at furniture options {time}",
        "Explore supermarket offers {time}",
    ],

    ("Finance", "High"): [
        "Pay credit card bill urgently {time}",
        "Transfer rent to landlord {time}",
        "Complete tax filing before deadline {time}",
        "Approve important payment {time}",
        "Resolve bank account issue {time}",
    ],
    ("Finance", "Medium"): [
        "Review monthly budget {time}",
        "Update expense tracker {time}",
        "Check investment portfolio {time}",
        "Plan savings for next month {time}",
        "Download bank statements {time}",
    ],
    ("Finance", "Low"): [
        "Explore new investment options {time}",
        "Read finance blog {time}",
        "Watch video on budgeting {time}",
        "Research mutual funds {time}",
        "Compare credit card offers {time}",
    ],
}


def generate_example(category, priority):
    """Generate one synthetic line: text, category, priority"""
    time_phrase = random.choice(TIME_PHRASES)
    templates = TEMPLATES[(category, priority)]
    template = random.choice(templates)

    # Insert time phrase
    if "{time}" in template:
        text = template.format(time=f"{time_phrase}")
    else:
        text = f"{template} {time_phrase}"

    return text, category, priority


def main():
    random.seed(42)
    rows = []

    # Aim for ~ balanced distribution
    target_rows = 3000
    per_combo = target_rows // (len(CATEGORIES) * len(PRIORITIES))  # ~1000 / 18 ≈ 55

    for category in CATEGORIES:
        for priority in PRIORITIES:
            for _ in range(per_combo):
                rows.append(generate_example(category, priority))

    # If less than 1000, fill remaining randomly
    while len(rows) < target_rows:
        category = random.choice(CATEGORIES)
        priority = random.choice(PRIORITIES)
        rows.append(generate_example(category, priority))

    random.shuffle(rows)

    # Write CSV
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category", "priority"])
        writer.writerows(rows)

    print(f"✅ Generated {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
