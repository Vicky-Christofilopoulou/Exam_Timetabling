# Exam_Timetabling

📚 **Exam Timetabling Project**

This is a Python-based implementation of the Exam Timetabling Problem for an academic scheduling scenario, featuring CSP algorithms and thorough comparisons.

---

### Problem Description

This project tackles the **exam timetabling problem**, a challenging constraint satisfaction problem (CSP). The goal is to schedule exams for specific courses during an exam period of **21 consecutive days**, while respecting several constraints:

- Each exam lasts **3 hours**.
- There are **three available time slots per day**: 9-12, 12-3, and 3-6.
- Only **one exam can be held at a time** (single available exam room).
- Courses from the **same semester** must be scheduled on different days.
- Some courses have **labs that must immediately follow their theoretical exam on the same day** (e.g., 12-3 theory, 3-6 lab).
- Exams for **“difficult” courses** must be at least **two days apart**.
- Exams for **courses taught by the same professor** must be on different days.

---

### What I Did

✅ **Implemented** three CSP algorithms:
- **Forward Checking (FC)**
- **Maintaining Arc Consistency (MAC)**
- **Min-Conflicts**

✅ Used the **MRV (Minimum Remaining Values)** heuristic and the **dom/wdeg** heuristic, based on:  
*"Boosting Systematic Search by Weighting Constraints" – Boussemart et al., 2004.*

✅ Based the implementation on the Python code from the AIMA repository:  
https://github.com/aimacode/aima-python/blob/master/csp.py  
(along with `utils.py` and `search.py`).

✅ Conducted **experimental comparisons** of the algorithms using provided data and defined appropriate **metrics**.

✅ Identified and discussed the **minimum possible exam period duration** for the given problem instance.

✅ Included **tables, metrics, and clear explanations of results**.

---

### How to Run

```python
python exam_timetabling.py

