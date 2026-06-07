import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(PROJECT_ROOT, "school.db")
SCHEMA_REF_FILE = os.path.join(PROJECT_ROOT, "db_schema_reference.txt")
MERMAID_REF_FILE = os.path.join(PROJECT_ROOT, "db_schema_mermaid.txt")

def init_database():
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print("Wiped old school.db trace completely for a clean slate.")
        except Exception as e:
            print(f"Notice: Database file locked, dropping tables inline instead. ({e})")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Building Relational Schema Architecture...")
    cursor.execute("CREATE TABLE grades (gradeid INTEGER PRIMARY KEY AUTOINCREMENT, GradeName TEXT NOT NULL);")
    
    cursor.execute("""
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_first_name TEXT NOT NULL,
        gender TEXT,
        student_last_name TEXT,
        dob TEXT,
        address TEXT,
        DayScholor INTEGER DEFAULT 1,
        HostelScholor INTEGER DEFAULT 0,
        grade_id INTEGER,
        FOREIGN KEY (grade_id) REFERENCES grades(gradeid)
    );""")

    cursor.execute("""
    CREATE TABLE Subjects_Grade (
        SubjectId INTEGER PRIMARY KEY AUTOINCREMENT,
        SubjectName TEXT NOT NULL,
        GradeId INTEGER,
        FOREIGN KEY (GradeId) REFERENCES grades(gradeid)
    );""")

    cursor.execute("""
    CREATE TABLE Marks (
        Student_Id INTEGER,
        GradeId INTEGER,
        SubjectId INTEGER,
        Mark REAL,
        FOREIGN KEY (Student_Id) REFERENCES students(student_id),
        FOREIGN KEY (GradeId) REFERENCES grades(gradeid),
        FOREIGN KEY (SubjectId) REFERENCES Subjects_Grade(SubjectId)
    );""")

    cursor.execute("""
    CREATE TABLE AdmissionFees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentId INTEGER,
        FiscalYear TEXT,
        AmountPaid REAL,
        FOREIGN KEY (StudentId) REFERENCES students(student_id)
    );""")

    cursor.execute("""
    CREATE TABLE TransportOpted (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentId INTEGER,
        RouteOpted TEXT,
        FiscalYear TEXT,
        FOREIGN KEY (StudentId) REFERENCES students(student_id)
    );""")

    cursor.execute("""
    CREATE TABLE TransportFeesDetails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Studentid INTEGER,
        Route TEXT,
        Amount REAL,
        DatePai TEXT,
        FiscalYear TEXT,
        FOREIGN KEY (Studentid) REFERENCES students(student_id)
    );""")

    cursor.execute("""
    CREATE TABLE HostelDetails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        studentId INTEGER,
        FiscalYear TEXT,
        FeesPaid REAL,
        FOREIGN KEY (studentId) REFERENCES students(student_id)
    );""")

    cursor.execute("CREATE TABLE Staff (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT, last_name TEXT, DOB TEXT);")

    cursor.execute("""
    CREATE TABLE Staff_Subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staffId INTEGER,
        Subjectid INTEGER,
        FOREIGN KEY (staffId) REFERENCES Staff(id),
        FOREIGN KEY (Subjectid) REFERENCES Subjects_Grade(SubjectId)
    );""")

    cursor.execute("""
    CREATE TABLE PTM_Report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        studentId INTEGER,
        GradeId INTEGER,
        staffId INTEGER,
        staffcomments TEXT,
        staffRating INTEGER,
        parentscomments TEXT,
        ParentsRatingToTeaching INTEGER,
        FOREIGN KEY (studentId) REFERENCES students(student_id),
        FOREIGN KEY (GradeId) REFERENCES grades(gradeid),
        FOREIGN KEY (staffId) REFERENCES Staff(id)
    );""")

    cursor.execute("CREATE TABLE Events (id INTEGER PRIMARY KEY AUTOINCREMENT, Event_Name TEXT, Date TEXT, More_Details TEXT);")

    print("Generating 500 records across active configurations...")
    for g in ['Grade 5', 'Middle School Grade 8', 'High School Grade 10', 'Senior Grade 12']:
        cursor.execute("INSERT INTO grades (GradeName) VALUES (?)", (g,))

    subjects_pool = [
        ('Computer Science', 1), ('English Literature', 1),
        ('Mathematics', 2), ('Social Studies', 2),
        ('General Science', 3), ('Regional Language', 3),
        ('Advanced Physics', 4), ('Chemistry', 4)
    ]
    cursor.executemany("INSERT INTO Subjects_Grade (SubjectName, GradeId) VALUES (?, ?)", subjects_pool)

    faculty_pool = [
        ('Rajesh', 'Kumar', '1984-05-14'), ('Anjali', 'Sharma', '1989-11-22'),
        ('Arun', 'Karthik', '1978-03-05'), ('Deepa', 'Srinivasan', '1992-08-19'),
        ('Sanjay', 'Mishra', '1981-04-12'), ('Priya', 'Nair', '1987-07-25')
    ]
    cursor.executemany("INSERT INTO Staff (first_name, last_name, DOB) VALUES (?, ?, ?)", faculty_pool)
    cursor.executemany("INSERT INTO Staff_Subject (staffId, Subjectid) VALUES (?, ?)", [(1,1), (2,2), (3,3), (4,5), (5,7), (6,8)])

    first_names_male = ['Aarav', 'Aditya', 'Arjun', 'Rahul', 'Vijay', 'Siddharth', 'Rohan', 'Vikram', 'Sai', 'Pranav']
    first_names_female = ['Diya', 'Sanya', 'Ananya', 'Meera', 'Kavitha', 'Priya', 'Shruti', 'Neha', 'Swathi', 'Riya']
    last_names = ['Mehta', 'Pillai', 'Krishnan', 'Iyer', 'Das', 'Rao', 'Nair', 'Joshi', 'Raghavan', 'Murugan']
    routes = ['Route North-Alpha', 'Route South-Beta', 'Route East-Gamma', 'Route West-Delta']
    streets = ['Thillai Nagar', 'KK Nagar', 'Cantonment', 'Velachery', 'Adyar', 'Anna Nagar']

    for i in range(1, 501):
        is_female = (i % 2 == 0)
        f_name = first_names_female[i % len(first_names_female)] if is_female else first_names_male[i % len(first_names_male)]
        l_name = last_names[(i * 3) % len(last_names)]
        gender = 'Female' if is_female else 'Male'
        grade_target = (i % 4) + 1
        is_hostel = 1 if (i % 5 == 0) else 0
        is_day = 0 if is_hostel == 1 else 1
        
        birth_year = 2015 if grade_target == 1 else (2012 if grade_target == 2 else (2010 if grade_target == 3 else 2008))
        dob_str = f"{birth_year}-0{((i%9)+1)}-{((i%20)+1):02d}"
        addr_str = f"{10 + (i%90)}, {streets[i % len(streets)]}, TN"

        cursor.execute("""
            INSERT INTO students (student_first_name, gender, student_last_name, dob, address, DayScholor, HostelScholor, grade_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (f_name, gender, l_name, dob_str, addr_str, is_day, is_hostel, grade_target))

        subj_1 = (grade_target * 2) - 1
        subj_2 = grade_target * 2
        base_modifier = (i % 45)
        score_1 = float(50 + base_modifier) if i % 15 != 0 else float(24 + (i % 10))
        score_2 = float(55 + (i % 40)) if i % 22 != 0 else float(28 + (i % 6))
        
        cursor.execute("INSERT INTO Marks (Student_Id, GradeId, SubjectId, Mark) VALUES (?, ?, ?, ?)", (i, grade_target, subj_1, min(score_1, 100.0)))
        cursor.execute("INSERT INTO Marks (Student_Id, GradeId, SubjectId, Mark) VALUES (?, ?, ?, ?)", (i, grade_target, subj_2, min(score_2, 100.0)))

        tuition_base = 25000.0 + (grade_target * 4000.0)
        cursor.execute("INSERT INTO AdmissionFees (StudentId, FiscalYear, AmountPaid) VALUES (?, '2026-2027', ?)", (i, tuition_base))
        
        if is_day == 1 and i % 3 == 0:
            selected_route = routes[i % len(routes)]
            cursor.execute("INSERT INTO TransportOpted (StudentId, RouteOpted, FiscalYear) VALUES (?, ?, '2026-2027')", (i, selected_route))
            cursor.execute("INSERT INTO TransportFeesDetails (Studentid, Route, Amount, DatePai, FiscalYear) VALUES (?, ?, 8500.0, '2026-05-15', '2026-2027')", (i, selected_route))
            
        if is_hostel == 1:
            hostel_charge = 60000.0 if i % 3 != 0 else None
            cursor.execute("INSERT INTO HostelDetails (studentId, FiscalYear, FeesPaid) VALUES (?, '2026-2027', ?)", (i, hostel_charge))

    cursor.execute("""
        INSERT INTO PTM_Report (studentId, GradeId, staffId, staffcomments, staffRating, parentscomments, ParentsRatingToTeaching)
        VALUES (1, 1, 1, 'Exemplary structural logic processing skills.', 5, 'Very pleased.', 5),
               (15, 2, 3, 'Core focus metrics can be extended under test limits.', 3, 'Will enforce tutoring frameworks.', 4);
    """)
    cursor.execute("INSERT INTO Events (Event_Name, Date, More_Details) VALUES ('Annual Tech Olympiad', '2026-07-20', 'Mass scale architecture validation checks.');")
    conn.commit()

    # Step 4: Extract explicit layout maps with hard newlines for the front-end parser
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    mermaid_code = "erDiagram\n"
    relation_lines = ""

    with open(SCHEMA_REF_FILE, "w", encoding="utf-8") as f_txt:
        f_txt.write("=== MASTER DATABASE COLD SCHEMA REFERENCE LAYER ===\n\n")
        
        for table in tables:
            f_txt.write(f"Table: {table}\n")
            mermaid_code += f"    {table} {{\n"
            
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            for col in columns:
                f_txt.write(f"  - Column: {col[1]} ({col[2]})\n")
                mermaid_code += f"        {col[2].lower()} {col[1]}\n"
                
            cursor.execute(f"PRAGMA foreign_key_list({table});")
            fkeys = cursor.fetchall()
            mermaid_code += "    }\n"
            
            for fk in fkeys:
                f_txt.write(f"  - Linkage Join: {fk[3]} references {fk[2]}({fk[4]})\n")
                relation_lines += f"    {table} ||--|| {fk[2]} : \"{fk[3]}\"\n"
            f_txt.write("\n")
            
    with open(MERMAID_REF_FILE, "w", encoding="utf-8") as f_mm:
        f_mm.write(mermaid_code + "\n" + relation_lines)
        
    conn.close()
    print("Relational schemas and layout references dynamically extracted.")

if __name__ == "__main__":
    init_database()