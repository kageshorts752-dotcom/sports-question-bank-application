# Sports Question Bank Application

 BCA Sports Technology 2026-2027

## Purpose
A web-based question repository for organising sports/physical-education questions by course, semester, subject, unit, topic, question type, difficulty, marks, Bloom's Taxonomy and tags.

## Technology
- Python
- Flask
- SQLite
- HTML/CSS/JavaScript

## Core Features
1. Add questions
2. Edit questions
3. Delete questions
4. Search questions
5. Filter by subject, difficulty, question type and Bloom level
6. Store tags and marks
7. Generate a random question set
8. Export the complete question bank to CSV
9. Responsive dashboard/table interface

## Run
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

The SQLite database `questions.db` is created automatically with sample records.

## Suggested Viva Points
- Why SQLite? It is lightweight and suitable for a student prototype.
- What is CRUD? Create, Read, Update and Delete.
- Why Bloom's Taxonomy? To classify the cognitive level of questions.
- What is the innovation? Random question-set generation plus multi-level filtering and CSV export.
