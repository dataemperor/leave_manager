import datetime
from collections import defaultdict


class Leave:
    """Represents a single leave request"""
    _LEAVE_TYPES = {'sick', 'annual', 'maternity'}
    _LEAVE_STATUS_TYPES = {'pending', 'approved', 'denied', 'cancelled'}

    def __init__(self, leave_date, leave_type, leave_status):
        """Initializes a Leave object

        Args:
            leave_date: Date of the leave
            leave_type: Type of leave
            leave_status: Status of leave

        Raises:
            ValueError: When the value for arguments leave_type or leave_status
                        aren't
                        in _LEAVE_TYPES or _LEAVE_STATUS_TYPES respectively
        """
        if leave_type not in Leave._LEAVE_TYPES:
            raise ValueError(
                "leave_type must be 'sick', 'annual' or 'maternity'")

        if leave_status not in Leave._LEAVE_STATUS_TYPES:
            raise ValueError(
                "leave_status must be " +
                "'pending', 'approved', 'denied' or 'cancelled'")

        self.leave_date = leave_date
        self.leave_type = leave_type
        self.leave_status = leave_status

    @property
    def status(self):
        return "Leave is currently " + self.leave_status

    @status.setter
    def status(self, newStatus):
        if newStatus not in Leave._LEAVE_STATUS_TYPES:
            raise ValueError(
                "leave_status must be " +
                "'pending', 'approved', 'denied' or 'cancelled'")
        self.leave_status = newStatus


class LeaveBalance:
    """Represents the Leave Balance"""

    def __init__(self, sick_leave: int = 0,
                 annual_leave: int = 0, maternity_leave: int = 0):
        """Initializes a LeaveBalance object

        Args:
            sick_leave: Number of sick leaves
            annual_leave: Number of annual leaves
            maternity_leave: Number of maternity leaves
        """
        self.__balance = defaultdict(int)
        self.__balance["sick"] = sick_leave
        self.__balance["annual"] = annual_leave
        self.__balance["maternity"] = maternity_leave

    @property
    def balance(self):
        return self.__balance

    def update_balance_by_days(self, increment_sick: int = 0,
                               increment_annual: int = 0,
                               increment_maternity: int = 0):
        """Updates leave balance

        Increments the leave_balance attribute of the Leave instance
        using three arguments whose values are defaulted to 0 (int)

        Args:
            increment_sick: Value to increment sick type leaves
            increment_annual: Value to increment annual type leaves
            increment_maternity: Value to increment maternity type leaves

        Raises:
            ValueError: Balance must be incremented using whole numbers
        """
        if not all(isinstance(val, int) for val in
                   [increment_sick,
                    increment_annual,
                    increment_maternity]):
            raise ValueError(
                'Balance must be incremented using whole numbers')

        self.__balance["sick"] += increment_sick
        self.__balance["annual"] += increment_annual
        self.__balance["maternity"] += increment_maternity


class Employee:

    def __init__(self, employee_name: str,
                 employee_leave_balance: LeaveBalance,
                 employee_leave_history: list[Leave]):
        self.employee_name = employee_name
        self.employee_leave_balance = employee_leave_balance
        self.employee_leave_history = employee_leave_history

    def get_leave_balance(self) -> LeaveBalance:
        return self.employee_leave_balance

    def request_leave(self, day: int, month: int, year: int,
                      request_leave_type, request_leave_status='pending'):
        """appends a new Leave object to attribute employee_leave_balance

        Takes in the day, month, year and type of the request
        with a status that defaults to 'pending'. Creates a
        datetime.date object using day, month and year.
        Uses the date.datetime object with the last two arguments
        to create a new Leave object if the date object isn't before
        the current date

        Args:
            day: Day of the requested leave.
            month: Month of the requested leave.
            year: Year of the requested leave.
            request_leave_type: Leave type of the requested leave.
            request_leave_status: Leave status of the requested leave.

        Raises:
            ValueError: A leave must be requested during or after the current
                        day

        """
        request_leave_date = datetime.date(year, month, day)
        current_day = datetime.date.today()

        if (request_leave_date < current_day):
            raise ValueError(
                "A leave must be requested during or after the current day")
        requested_leave = Leave(
            request_leave_date, request_leave_type, request_leave_status)

        self.employee_leave_history.append(requested_leave)

    def cancel_leave(self, day: int, month: int, year: int):
        """Removing a leave from leave_history using a date

        Takes in day, month and year as arguments, creates a date using
        them. Then the length of employee_leave_history taken to confirm
        if any leaves were removed from it. Then a new list of list is
        created using employee_leave_history but if a Leave object within
        has a date that matches cancel_leave_date, it isn't included
        within the new list, then the new list is assigned to the object's
        employee_leave_list parameter. Whether any Leave objects were cancelled
        are decided by comparing the length of the previous leave history
        attribute with the length of the current employee_leave_history
        attribute.

        Args:
            day: Day of the leave cancellation request.
            month: Month of the leave cancellation request.
            year: Year of the leave cancellation request.
        """
        cancel_leave_date = datetime.date(year, month, day)
        original_leave_history_length = len(self.employee_leave_history)

        self.employee_leave_history = \
            [leave for leave in self.employee_leave_history
             if leave.leave_date != cancel_leave_date]

        if (original_leave_history_length == len(self.employee_leave_history)):
            print("Leave cancellation was unsuccessful")

    def get_leave_history(self) -> list[Leave]:
        """returns employee_leave_history

        Returns:
            employee_leave_history of the object of type list[Leave]
        """
        return self.employee_leave_history
