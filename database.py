import sqlite3
import datetime
from employee import Employee
from employee import Leave
from employee import LeaveBalance


class Database:
    def __init__(self, sqliteDB_file_path):
        self.sqliteDB_file_path = sqliteDB_file_path
        self.connection = None
        self.cursor = None

    def connect_to_database(self):
        try:
            self.connection = sqlite3.connect(self.sqliteDB_file_path)
            self.connection.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.connection.cursor()
            print(f"Connected to {self.sqliteDB_file_path}")
            return self.connection
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            self.connection = None
            self.cursor = None
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_tables(self):
        if not self.connection or not self.cursor:
            print("Not connected to the database")
            return

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_balances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER UNIQUE,
        sick_days INTEGER DEFAULT 0,
        annual_days INTEGER DEFAULT 0,
        maternity_days INTEGER DEFAULT 0,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        leave_date TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        leave_status TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
        ''')
        self.connection.commit()

    def create_employee(self, employee: Employee):
        if not self.connection or not self.cursor:
            print("Not connected to the database or cursor not available")
            return

        try:
            # Inserting name into employees table
            self.cursor.execute("INSERT INTO employees (name) VALUES (?)",
                                (employee.employee_name,))

            employee_id = self.cursor.lastrowid
            self.connection.commit()

            # Inserting intial leave balance
            balance = employee.employee_leave_balance.balance
            self.cursor.execute("""
            INSERT INTO leave_balances (employee_id, sick_days, annual_days, maternity_days)
            VALUES (?, ?, ?, ?)
            """, (employee_id, balance['sick'],
                  balance['annual'],
                  balance['maternity']))
            self.connection.commit()

            # inserting initial leave history
            for leave_entry in employee.employee_leave_history:
                self.cursor.execute(
                    """
                    INSERT INTO leave (employee_id, leave_date, leave_type, leave_status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (employee_id, leave_entry.leave_date.isoformat(),
                     leave_entry.leave_type, leave_entry.leave_status))

            self.connection.commit()
        except sqlite3.IntegrityError:
            print("Employee already exists")

        except sqlite3.Error as e:
            print(f"Error creating Employee:{e}")

    def select_leave_balance_by_name(self, employee_name: str):
        """
        Selecting leave balance from the employee table where id matches
        """
        if not self.connection or not self.cursor:
            print("Not connected to the database or cursor not available")
            return None

        try:
            self.cursor.execute(
                """
                SELECT lb.sick_days, lb.annual_days, lb.maternity_days
                FROM employees e
                JOIN leave_balances lb ON e.id = lb.employee_id
                WHERE e.name = ?
                """, (employee_name,)
            )
            result = self.cursor.fetchone()
            if result:
                sick, annual, maternity = result
                return LeaveBalance(sick_leave=sick, annual_leave=annual, maternity_leave=maternity)
            else:
                print(f"No leave balance found for employee {employee_name}")
                return None

        except sqlite3.Error as e:
            print(f"{e}")
            return None

    def request_leave_by_name(self, employee_name: str, leaves: list[Leave]):
        """
        Creating one or more leaves from the employee table where id matches
        """
        if not self.connection or not self.cursor:
            print("Not connected to the database or cursor not available")
            return

        try:
            self.cursor.execute("""
            SELECT id
            FROM employees
            WHERE name = ?
            """, (employee_name,))
            employee_id_row = self.cursor.fetchone()

            if not employee_id_row:
                print(f"Error: Employee {employee_name} not found")
                return

            employee_id = employee_id_row[0]

            for leave_request in leaves:
                self.cursor.execute(
                    """
                    INSERT INTO Leave (employee_id, leave_date, leave_type, leave_status)
                    VALUES (?, ? ,? , ?)
                    """, (employee_id, leave_request.leave_date.isoformat(),
                          leave_request.leave_type, leave_request.leave_status)
                )

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"{e}")

    def cancel_leave_by_name(self, employee_name: str, leave_dates: list[datetime.date]):
        """
        Cancelling one or more leaves from the employee table where id matches
        """
        if not self.connection or not self.cursor:
            print("Not connected to the database or cursor not available")
            return None

        try:
            self.cursor.execute(
                """
                SELECT id
                FROM employees
                WHERE name = ?
                """, (employee_name, )
            )
            employee_id_row = self.cursor.fetchone()

            if not employee_id_row:
                print(f"Employee {employee_name} not found")
                return

            employee_id = employee_id_row[0]
            rows_deleted = 0
            for date_to_cancel in leave_dates:
                self.cursor.execute(
                    """
                    DELETE FROM leave
                    WHERE employee_id = ? AND leave_date = ?
                    """, (employee_id, date_to_cancel.isoformat())
                )
                rows_deleted += self.cursor.rowcount

            self.connection.commit()

            if rows_deleted > 0:
                print(f"Cancelled {rows_deleted} for employee {employee_name}")
            else:
                print(f"No leave for employee {employee_name}")

        except sqlite3.Error as e:
            print(f"{e}")

    def view_leave_by_name(self, employee_name) -> list[Leave]:
        """
        Selecting leave history according from the employee table where id matches
        """
        if not self.connection or not self.cursor:
            print("Not connected to the database or cursor not available")
            return []

        leave_history = []
        try:
            self.cursor.execute("""
            SELECT id
            FROM employees
            WHERE name = ?
            """, (employee_name, ))
            employee_id_row = self.cursor.fetchone()

            if not employee_id_row:
                print(f'Error viewing {employee_name}')
                return []

            employee_id = employee_id_row[0]

            self.cursor.execute("""
            SELECT leave_date, leave_type, leave_status
            FROM leave
            WHERE employee_id = ?
            ORDER BY leave_date ASC
            """, (employee_id, ))
            results = self.cursor.fetchall()

            for row in results:
                leave_date_str, leave_type, leave_status = row
                leave_date = datetime.date.fromisoformat(leave_date_str)
                leave_history.append(
                    Leave(leave_date, leave_type, leave_status))
            return leave_history

        except sqlite3.Error as e:
            print(f"Error viewing leaves {employee_name}: {e}")
            return []
