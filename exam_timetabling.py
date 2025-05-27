from csp import *
from tabulate import tabulate
import time
import csv

class Exam_Timetabling(CSP):
    def __init__(self, days, csv_file):

        # Read the data from the csv file
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader)          # skip header
            for row in reader:
                rows.append(row)

        print("Αρχείο CSV:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # For each class we have 4 columns we need to store. We do not store if it has a lab, only to process it
        self.semester = []
        self.variables = []
        self.professors = []
        self.difficulty = []

        for row in rows:  # Process each row in the file
            self.semester.append(int(row[0]))   # Column 1: Semester
            self.variables.append(row[1])       # Column 2: Class name
            self.professors.append(row[2])      # Column 3: Professor's name

            # Column 4: Difficulty (True / False)
            if row[3] == 'FALSE':
                self.difficulty.append(False)
            else:
                self.difficulty.append(True)

            # Column 5: Has a lab (True / False)
            if row[4] == 'TRUE':

                # We create a new class with name e.g. lesson_Lab
                lab_course = row[1] + '_Lab'
                self.variables.append(lab_course)
                self.professors.append(row[2])      # Lab has the same professor
                self.semester.append(int(row[0]))   # Lab has the same semester
                self.difficulty.append(False)       # We assume lab is not difficult otherwise it will not be possible to place it right after the theory

        # Create dictionaries for semester, professor, and difficulty
        # in order to use them for the constraints
        self.lesson_semester = dict(zip(self.variables, self.semester))
        self.lesson_professors = dict(zip(self.variables, self.professors))
        self.lesson_difficulty = dict(zip(self.variables, self.difficulty))

        # Slot setup: 3 time slots per day
        slots = ["9-12", "12-3", "3-6"]

        # Create all possible combinations for days and slots
        all_slots = [(day, slot) for day in range(1, days + 1) for slot in slots]

        # There are 3 types of classes.
        # 1. A class that doesn't have a lab, so it can go at any slot.
        lab_not_exists = all_slots

        # 2. A class that has a lab, so it can not be scheduled at the last slot of every day
        lab_exists = []
        for slot in all_slots:
            if slot[1] != "3-6":  # Lab should not be scheduled in the last slot of the day
                lab_exists.append(slot)

        # 3. A lab class can not be scheduled at the first stol of each day.
        lab = []
        for slot in all_slots:
            if slot[1] != "9-12":  # Lab should not be scheduled in the first slot of the day
                lab.append(slot)

        # Now we iterate all classes and assign the corresponding domain.
        self.domains = {}
        for lesson in self.variables:
            lab_lesson = lesson + '_Lab'
            if lab_lesson in self.variables:  # Theory lesson has lab
                self.domains[lesson] = lab_exists
            elif '_Lab' in lesson:  # Check if this is a lab class
                self.domains[lesson] = lab
            else:
                self.domains[lesson] = lab_not_exists

        # Now we create the neighbors for each class
        # Two lessons are neighbors if there are in at least one constrain (Piazza comment)
        self.neighbors = {}
        for lesson in self.variables:
            neighbor = []  # Add all the other lessons, except of itself
            for lesson2 in self.variables:
                if lesson2 != lesson:
                    # Check if they share at least one constraint
                    same_semester = self.lesson_semester[lesson] == self.lesson_semester[lesson2]
                    same_professor = self.lesson_professors[lesson] == self.lesson_professors[lesson2]
                    both_difficult = self.lesson_difficulty[lesson] and self.lesson_difficulty[lesson2]
                    theory_lab_pair = (
                            lesson + '_Lab' == lesson2 or lesson == lesson2 + '_Lab'
                    )

                    if same_semester or same_professor or both_difficult or theory_lab_pair:
                        neighbor.append(lesson2)
                        self.neighbors[lesson] = neighbor

        # Counter for the constraints
        self.constraints_checked = 0

        # Initialize CSP instance
        CSP.__init__(self, self.variables, self.domains, self.neighbors, self.constraints)

    # A function f(A, a, B, b) that returns true if neighbors
    # A, B satisfy the constraint when they have values A=a, B=b
    def constraints(self, A, a, B, b):
        self.constraints_checked += 1

        # A dictionary to map the time slots ("9-12", "12-3", "3-6") to numerical values
        slot_map = {
            "9-12": 1,
            "12-3": 2,
            "3-6": 3
        }

        # Constraint: Two courses cannot be at the same time
        if a == b:
            return False

        # Constraint: Labs must follow theory exams on the same day
        if A + '_Lab' in self.variables:    # A is theory lesson
            if B == A + '_Lab':             # B is lab
                if (b[0] == a[0]) and (slot_map[b[1]] == (slot_map[a[1]] + 1)):  # lab is right after theory
                    return True
                else:
                    return False

        if B + '_Lab' in self.variables:    # B is theory lesson
            if A == B + '_Lab':             # A is lab
                if (a[0] == b[0]) and (slot_map[a[1]] == (slot_map[b[1]] + 1)):
                    return True
                else:
                    return False

        # Constraint: Difficult courses should have at least 2 days in between
        if self.lesson_difficulty[A] and self.lesson_difficulty[B]:
            if abs(a[0] - b[0]) <= 2:  # Less than two days apart
                return False

        # Constraint: Courses of the same semester should be on different days
        if self.lesson_semester[A] == self.lesson_semester[B]:
            if abs(a[0] - b[0]) == 0:  # Exam on the same day
                return False

        # Constraint: Courses by the same professor must be on different days
        if self.lesson_professors[A] == self.lesson_professors[B]:
            if abs(a[0] - b[0]) == 0:  # Exam on the same day
                return False
        return True  # none of the constraints were violated

def print_solution_table(solution, days):
    # Map slot times to their order (index) for sorting purposes
    slot_order = {
        "9-12": 1,
        "12-3": 2,
        "3-6": 3
    }

    day_schedule = {day: [] for day in range(1, days+1)}  # Create a schedule dictionary for each day

    # Group courses by day
    for course, (day, slot) in solution.items():
        day_schedule[day].append((course, slot))

    # Prepare data for tabulation
    table_data = []
    for day, courses in day_schedule.items():
        if courses:
            # Sort courses by their slot order
            sorted_courses = sorted(courses, key=lambda x: slot_order[x[1]])
            for course, slot in sorted_courses:
                table_data.append([day, course, slot])

    # Print the schedule table
    print(tabulate(table_data, headers=["Day", "Course", "Time Slot"], tablefmt="grid"))


def solve_timetabling(problem, days):

    # -------------- Backtracking + MRV + Forward Checking --------------------
    print("Solving with backtracking + MRV + Forward Checking:")
    start_time = time.time()
    solution_fc = backtracking_search(csp = problem, select_unassigned_variable = mrv, order_domain_values = lcv , inference = forward_checking)
    elapsed_time_fc = time.time() - start_time
    if solution_fc is None:
        print("No solution found!")
        return

    print_solution_table(solution_fc, days)
    print(f"Time Taken: {elapsed_time_fc:.4f}s")
    total_assigns_fc = problem.nassigns
    constraints_fc = problem.constraints_checked
    backtracks_fc = problem.backtracks
    nodes_visited_fc = problem.nodes_visited
    print(f"Total nassigns: {total_assigns_fc}\n")
    print(f"Total Backtracks: {backtracks_fc}")
    print(f"Constraints checked: {constraints_fc}\n")
    print(f"Nodes visited: {nodes_visited_fc}\n")

    # -------------- Backtracking + dom/wdeg + Forward Checking --------------------
    print("Solving with backtracking + dom/wdeg + Forward Checking:")
    start_time = time.time()
    solution_fc2 = backtracking_search(csp = problem, select_unassigned_variable = domwdeg, order_domain_values = lcv , inference = forward_checking)
    elapsed_time_fc2 = time.time() - start_time
    if solution_fc2 is None:
        print("No solution found!")
        return

    print_solution_table(solution_fc2, days)
    print(f"Time Taken: {elapsed_time_fc2:.4f}s")
    total_assigns_fc2 = problem.nassigns
    constraints_fc2 = problem.constraints_checked
    backtracks_fc2 = problem.backtracks
    nodes_visited_fc2 = problem.nodes_visited
    print(f"Total Backtracks: {backtracks_fc2}")
    print(f"Total nassigns: {total_assigns_fc2}\n")
    print(f"Constraints checked: {constraints_fc2}\n")
    print(f"Nodes visited: {nodes_visited_fc2}\n")


    # -------------- Backtracking + MRV + MAC --------------------
    problem.constraints_checked = 0
    print("Solving with backtracking + MRV + MAC:")
    start_time = time.time()
    solution_mac = backtracking_search(csp = problem, select_unassigned_variable = mrv, order_domain_values = lcv , inference = mac)
    elapsed_time_mac = time.time() - start_time
    if solution_mac is None:
        print("No solution found!")
        return

    print_solution_table(solution_mac, days)
    print(f"Time Taken: {elapsed_time_mac:.4f}s")
    total_assigns_mac = problem.nassigns
    constraints_mac = problem.constraints_checked
    backtracks_mac = problem.backtracks
    nodes_visited_mac = problem.nodes_visited
    print(f"Total Backtracks: {backtracks_mac}")
    print(f"Total nassigns: {total_assigns_mac}\n")
    print(f"Constraints checked: {constraints_mac}\n")
    print(f"Nodes visited: {nodes_visited_mac}\n")

    # -------------- Backtracking + dom/wdeg + MAC --------------------
    problem.constraints_checked = 0
    print("Solving with backtracking + dom/wdeg + MAC:")
    start_time = time.time()
    solution_mac2 = backtracking_search(csp=problem, select_unassigned_variable = domwdeg, order_domain_values=lcv,
                                       inference=mac)
    elapsed_time_mac2 = time.time() - start_time
    if solution_mac2 is None:
        print("No solution found!")
        return

    print_solution_table(solution_mac2, days)
    print(f"Time Taken: {elapsed_time_mac2:.4f}s")
    total_assigns_mac2 = problem.nassigns
    constraints_mac2 = problem.constraints_checked
    nodes_visited_mac2 = problem.nodes_visited
    backtracks_mac2 = problem.backtracks
    print(f"Total Backtracks: {backtracks_mac2}")
    print(f"Total nassigns: {total_assigns_mac2}\n")
    print(f"Constraints checked: {constraints_mac2}\n")
    print(f"Nodes visited: {nodes_visited_mac2}\n")

    # ----------------- Min Conflicts -----------------------
    problem.constraints_checked = 0
    print("Solving with Min Conflicts:")
    start_time = time.time()
    solution_min_conflicts = min_conflicts(problem, max_steps=5000)
    elapsed_time_min_conflicts = time.time() - start_time
    if solution_min_conflicts is None:
        print("No solution found!")
        return

    print_solution_table(solution_min_conflicts, days)
    print(f"Time Taken: {elapsed_time_min_conflicts:.4f}s")
    total_assigns_min_conflicts = problem.nassigns
    constraints_min_conflicts = problem.constraints_checked
    nodes_visited_min_conflicts = problem.nodes_visited
    backtracks_min_conflicts = problem.backtracks
    print(f"Total Backtracks: {backtracks_min_conflicts}")
    print(f"Total nassigns: {total_assigns_min_conflicts}\n")
    print(f"Constraints checked: {constraints_min_conflicts}\n")
    print(f"Nodes visited: {nodes_visited_min_conflicts}\n")

    print("Summary:")
    print(f"{'Algorithm':<20}{'Time (s)':<12}{'Total nassigns':<15}{'Constraints Checked':<20}{'Backtracks':^20}{'Nodes Visits':^20}")
    print("-" * 120)
    print(f"{'FC + MRV':<20}{elapsed_time_fc:.4f}s\t{total_assigns_fc:^20}{constraints_fc:^20}{backtracks_fc:^20}{nodes_visited_fc:^20}")
    print(f"{'FC + DOM/WDEG':<20}{elapsed_time_fc2:.4f}s\t{total_assigns_fc2:^20}{constraints_fc2:^20}{backtracks_fc2:^20}{nodes_visited_fc2:^20}")
    print(f"{'MAC + MRV':<20}{elapsed_time_mac:.4f}s\t{total_assigns_mac:^20}{constraints_mac:^20}{backtracks_mac:^20}{nodes_visited_mac:^20}")
    print(f"{'MAC + DOM/WDEG':<20}{elapsed_time_mac2:.4f}s\t{total_assigns_mac2:^20}{constraints_mac2:^20}{backtracks_mac2:^20}{nodes_visited_mac2:^20}")
    print(f"{'Min Conflicts':<20}{elapsed_time_min_conflicts:.4f}s\t{total_assigns_min_conflicts:^20}{constraints_min_conflicts:^20}{backtracks_min_conflicts:^20}{nodes_visited_min_conflicts:^20}")



if __name__ == '__main__':
    # Instantiate the Exam_Timetabling class and solve
    d = 17                  # Days that the exams will last
    file = 'h3-data.csv'    # File that has all the data
    problem = Exam_Timetabling(d, file)
    solve_timetabling(problem, d)
