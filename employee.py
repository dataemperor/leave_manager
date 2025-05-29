import datetime


class Employee:

    def __init__(self, employee_name, employee_leave_balance: dict,
                 employee_leave_history: datetime.date):
        self.employee_name = employee_name
        self.employee_leave_balance = employee_leave_balance
        self.employee_leave_history = employee_leave_history

    @property
    def name(self):
        return self.employee_name

    @property
    def leave_balance(self):
        return self.employee_leave_balance

    @property
    def leave_history(self):
        return self.employee_leave_history

    def days_from_last_leave(self):
        last_leave_days = datetime.date.today() - self.employee_leave_history
        return last_leave_days


class Leave:
    LEAVE_TYPES = {'sick', 'annual', 'maternity'}

    def __init__(self, leave_type: str, leave_date: datetime.date):
        if leave_type not in self.LEAVE_TYPES:
            raise ValueError(f"attribute leave_type cannot be {leave_type}")
        self.leave_type = leave_type
        self.leave_date = leave_date

    @property
    def type(self):
        """Get leave type"""
        return self.leave_type

    @property
    def date(self):
        """Get leave date"""
        return self.leave_date


employee_name = "Jayathu"
employee_leave_balance = {"sick": 5, "annual": 1, "maternity": 0}
employee_leave_history = datetime.date.today()

Jayathu = Employee(employee_name, employee_leave_balance,
                   employee_leave_history)

print(Jayathu.employee_leave_balance)
print(Jayathu.leave_history)
print(Jayathu.days_from_last_leave())
