from datetime import date
from dateutil.relativedelta import relativedelta

class OpenCollective:
    
    @staticmethod
    async def get_open_collective_data():
        return
    
    @staticmethod
    async def average_total_income() -> int:
        return

    @staticmethod
    async def average_total_outgoing() -> int:
        return
    
    @staticmethod
    async def current_balance() -> int:
        return
    
    @staticmethod
    async def forecast_negative_cashflow_date(start_balance: int, incoming: int, outgoing: int) -> int:
        months = 0
        while start_balance > 0 and months <= 60:
            start_balance += incoming
            start_balance -= outgoing
            months += 1

        return (date.today() + relativedelta(months=+months)).strftime("%B")
    