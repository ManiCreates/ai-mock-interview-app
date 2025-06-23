# ai_mockapp_with_sql_and_aptitude.py
import streamlit as st
import speech_recognition as sr
import sqlite3
from datetime import datetime
import time

# --------------------- DB SETUP ---------------------
def init_db():
    conn = sqlite3.connect("interview_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interview_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            time TEXT,
            topic TEXT,
            subtopic TEXT,
            sub_subtopic TEXT,
            question TEXT,
            answer TEXT,
            tip TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --------------------- Voice Input ---------------------
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now.")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success("✅ Voice captured.")
            return text
        except sr.WaitTimeoutError:
            st.error("⌛ Timeout. You were silent.")
        except sr.UnknownValueError:
            st.error("🤔 Could not understand.")
        except sr.RequestError:
            st.error("⚠️ Connection problem.")
    return ""

# --------------------- Questions ---------------------
questions = {
    "Technical Round": {
        "Programming Basics": [
            ("What is a variable in Python?", "Explain variables with example."),
            ("Difference between list and tuple?", "List is mutable, tuple is not."),
        ],
        "OOP Concepts": [
            ("What is inheritance?", "Explain with real-world example."),
            ("What is abstraction vs encapsulation?", "Give key differences."),
        ],
        "Data Structures": [
            ("What is a stack?", "LIFO, use push/pop."),
            ("Linked list vs array?", "Linked list uses pointers."),
        ],
        "Database": [
            ("What is a primary key?", "Uniquely identifies a row."),
            ("Write a SQL query to fetch names.", "SELECT name FROM table_name;"),
        ],
        "Full Stack Web Development": {
            "Frontend": [
                ("What is HTML used for?", "Structure of web pages."),
                ("Difference between id and class in CSS?", "ID is unique; class can be reused."),
            ],
            "Backend": [
                ("What is REST API?", "Interface for client-server interaction."),
                ("What is Node.js?", "JavaScript runtime for backend."),
            ],
            "Database": [
                ("What is MongoDB?", "NoSQL database."),
                ("Difference between SQL and NoSQL?", "Structured vs flexible schema."),
            ]
        },
        "Cloud Computing": {
            "Easy": [
                ("What is cloud computing?", "It is the delivery of computing services over the internet."),
                ("Name some common cloud service providers.", "Examples: AWS, Microsoft Azure, Google Cloud."),
                ("What are the main cloud service models?", "IaaS, PaaS, SaaS — Infrastructure, Platform, Software."),
                ("What are public, private, and hybrid clouds?", "Public is shared, private is internal, hybrid is mix of both."),
                ("What is scalability in cloud?", "Ability to increase/decrease resources as needed."),
            ],
            "Medium": [
                ("Explain IaaS, PaaS, and SaaS with examples.", "IaaS = AWS EC2, PaaS = Google App Engine, SaaS = Gmail."),
                ("What is virtualization in cloud?", "Creating virtual servers from physical resources."),
                ("Difference between elasticity and scalability?", "Elasticity auto-adjusts; scalability is planned growth."),
                ("What is serverless computing?", "Run code without managing servers. Example: AWS Lambda."),
                ("What is load balancing in cloud?", "Distributes traffic for high availability."),
            ],
            "Tough": [
                ("How does cloud ensure data security?", "Using encryption, IAM roles, firewall rules."),
                ("What are containers in cloud?", "Lightweight environments like Docker."),
                ("Explain multi-tenancy in cloud.", "Many users share same resources securely."),
                ("What is a Virtual Private Cloud (VPC)?", "Private network in cloud, isolated."),
                ("How does disaster recovery work in cloud?", "Use backups, failovers, replication."),
            ]
        }
    },
    "HR Round": [
        ("Tell me about yourself.", "Background, skills, goals."),
        ("Why should we hire you?", "Match your skills with the job."),
        ("What are your strengths and weaknesses?", "Be honest and show growth."),
    ],
    "Aptitude": {
        "Easy": [
            ("What is 25% of 200?", ["25", "50", "75", "100"], "50"),
            ("Which number is a multiple of both 2 and 3?", ["4", "6", "9", "10"], "6"),
            ("What is the average of 10, 20, 30?", ["15", "20", "25", "30"], "20"),
        ],
        "Tough": [
            ("If a train runs 120 km in 2 hours, what is its speed in m/s?", ["16.67", "60", "33.33", "20"], "16.67"),
            ("Find the compound interest on Rs.1000 at 10% for 2 years.", ["100", "200", "210", "220"], "210"),
            ("A can do a work in 20 days, B in 30 days. How long together?", ["12", "15", "10", "18"], "12"),
        ]
    }
}

# --------------------- Session State ---------------------
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'timer_started' not in st.session_state:
    st.session_state.timer_started = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'voice_input' not in st.session_state:
    st.session_state.voice_input = ""

# --------------------- UI ---------------------
st.title("🧠 AI Mock Interview & Aptitude App")

if not st.session_state.interview_started:
    name = st.text_input("Enter your Name:", max_chars=50)
    email = st.text_input("Enter your Email:", max_chars=100)
    main_topic = st.selectbox("Choose Interview Type:", ["Technical Round", "HR Round", "Aptitude"])

    subtopic = None
    sub_subtopic = None

    if main_topic == "Technical Round":
        subtopic = st.selectbox("Select Technical Subtopic", [
            "Programming Basics", "OOP Concepts", "Data Structures", "Database", 
            "Full Stack Web Development", "Cloud Computing"
        ])
        if subtopic == "Full Stack Web Development":
            sub_subtopic = st.selectbox("Choose Sub-Area", ["Frontend", "Backend", "Database"])
        elif subtopic == "Cloud Computing":
            sub_subtopic = st.selectbox("Choose Level", ["Easy", "Medium", "Tough"])
    elif main_topic == "Aptitude":
        subtopic = st.selectbox("Choose Aptitude Level", ["Easy", "Tough"])

    if st.button("Start Interview/Test"):
        if not name or not email:
            st.warning("Please enter both name and email.")
        else:
            st.session_state.interview_started = True
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.session_state.selected_main_topic = main_topic
            st.session_state.selected_subtopic = subtopic
            st.session_state.selected_sub_subtopic = sub_subtopic
            st.session_state.question_index = 0
            st.session_state.answers = []
            st.session_state.timer_started = False
            st.session_state.voice_input = ""
            st.rerun()

# --------------------- Interview Logic ---------------------
if st.session_state.interview_started:
    topic = st.session_state.selected_main_topic
    subtopic = st.session_state.selected_subtopic
    sub_subtopic = st.session_state.selected_sub_subtopic
    index = st.session_state.question_index

    if topic == "Technical Round":
        if subtopic == "Full Stack Web Development" or subtopic == "Cloud Computing":
            topic_questions = questions[topic][subtopic][sub_subtopic]
        else:
            topic_questions = questions[topic][subtopic]

        if index < len(topic_questions):
            question, tip = topic_questions[index]
            st.markdown(f"**🧑 Interviewer:** {question}")

            st.markdown("🎤 Speak or type your answer:")
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("🎙️ Speak Now"):
                    st.session_state.voice_input = get_voice_input()
            with col2:
                user_input = st.text_area("✍️ Or type here:", value=st.session_state.voice_input)

            if st.button("Submit Answer"):
                st.session_state.answers.append((question, user_input, tip))
                st.session_state.question_index += 1
                st.session_state.voice_input = ""
                st.rerun()
        else:
            st.success("✅ Interview Completed")

    elif topic == "HR Round":
        topic_questions = questions[topic]
        if index < len(topic_questions):
            question, tip = topic_questions[index]
            st.markdown(f"**🧑 Interviewer:** {question}")
            user_input = st.text_area("✍️ Your Answer:")
            if st.button("Submit Answer"):
                st.session_state.answers.append((question, user_input, tip))
                st.session_state.question_index += 1
                st.rerun()
        else:
            st.success("✅ Interview Completed")

    elif topic == "Aptitude":
        topic_questions = questions[topic][subtopic]
        if index < len(topic_questions):
            question, options, correct = topic_questions[index]

            if not st.session_state.timer_started:
                st.session_state.start_time = time.time()
                st.session_state.timer_started = True

            elapsed = time.time() - st.session_state.start_time
            remaining = int(180 - elapsed)

            if remaining > 0:
                st.markdown(f"**⏱ Time Left: {remaining} seconds**")
                st.markdown(f"**Q{index+1}: {question}**")
                user_input = st.radio("Choose an answer:", options)

                if st.button("Submit Answer"):
                    st.session_state.answers.append((question, user_input, f"Correct: {correct}"))
                    st.session_state.question_index += 1
                    st.session_state.timer_started = False
                    st.rerun()
            else:
                st.warning("⏰ Time up for this question!")
                st.session_state.answers.append((question, "No Answer (Timed Out)", f"Correct: {correct}"))
                st.session_state.question_index += 1
                st.session_state.timer_started = False
                st.rerun()
        else:
            st.success("✅ Aptitude Test Completed")

    # --- Fixed total questions count check ---
    if topic == "Technical Round":
        if subtopic in ["Full Stack Web Development", "Cloud Computing"] and sub_subtopic:
            total_questions = len(questions[topic][subtopic][sub_subtopic])
        else:
            total_questions = len(questions[topic][subtopic])
    elif topic == "Aptitude":
        total_questions = len(questions[topic][subtopic])
    else:
        total_questions = len(questions[topic])
    if index >= total_questions:
        st.subheader("📄 Summary")
        for i, entry in enumerate(st.session_state.answers):
            q = entry[0] if len(entry) > 0 else ""
            a = entry[1] if len(entry) > 1 else ""
            t = entry[2] if len(entry) > 2 else ""

            st.markdown(f"**Q{i+1}: {q}**")

            if isinstance(t, str) and "Correct:" in t:
                correct_answer = t.split("Correct: ")[1].strip()
                is_correct = a.strip() == correct_answer
                result_icon = "✅ Correct" if is_correct else f"❌ Wrong (Correct: {correct_answer})"
                st.markdown(f"- 📝 Your Answer: {a}")
                st.markdown(f"- 📌 Result: {result_icon}")
            else:
                st.markdown(f"- 📝 Your Answer: {a}")
                st.markdown(f"- 💡 {t}")

        # ---------- Save to SQLite ----------
        conn = sqlite3.connect("interview_data.db")
        c = conn.cursor()
        for q, a, t in st.session_state.answers:
            c.execute('''
                INSERT INTO interview_logs (name, email, time, topic, subtopic, sub_subtopic, question, answer, tip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                st.session_state.user_name,
                st.session_state.user_email,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                topic,
                subtopic,
                sub_subtopic if topic == "Technical Round" and subtopic in ["Full Stack Web Development", "Cloud Computing"] else None,
                q,
                a,
                t
            ))
        conn.commit()
        conn.close()

        # ---------- Save to TXT File ----------
        with open("interview_logs.txt", "a", encoding="utf-8") as f:
            f.write("\n--- New Interview/Test ---\n")
            f.write(f"Name: {st.session_state.user_name}\n")
            f.write(f"Email: {st.session_state.user_email}\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Topic: {topic}, Subtopic: {subtopic}, Sub-Subtopic: {sub_subtopic}\n\n")
            for i, (q, a, t) in enumerate(st.session_state.answers):
                f.write(f"Q{i+1}: {q}\nAnswer: {a}\nTip/Correct: {t}\n\n")

        st.success("📁 Your responses have been saved to database and text file!")
        st.session_state.interview_started = False
