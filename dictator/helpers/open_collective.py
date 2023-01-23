from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from constants import OC_GRAPHQL_ENDPOINT, OC_GRAPHQL_KEY, OC_ANALYSIS_PERIOD_MONTHS
import requests
import json

class OpenCollective:
    """"""
    
    def __get_data_time_period(period_months: int) -> tuple[datetime]:
        
        now = datetime.now()
        
        start_month = now - relativedelta(months=period_months, days=now.day - 1)
        first_second_start_month = datetime.combine(start_month, time.min)
        
        first_day_this_month = now.replace(day=1)
        last_day_last_month = first_day_this_month - relativedelta(days=1)
        last_second_last_month = datetime.combine(last_day_last_month, time.max)
        
        return (first_second_start_month, last_second_last_month)


    def __get_open_collective_data(period_range: tuple[datetime]) -> dict:
        
        dateFrom = period_range[0].isoformat() + "Z"
        dateTo = period_range[1].isoformat() + "Z"
        
        varibles = {
            "dateFrom": dateFrom,
            "dateTo": dateTo
        }
        
        query = """
        query($dateFrom: DateTime, $dateTo: DateTime) {
            collective(slug: "twohoursonelife") {
                stats {
                    balance {
                        value
                    }
                }
            }
            transactions(
                account: [{ slug: "twohoursonelife" }]
                dateFrom: $dateFrom
                dateTo: $dateTo
            )   {
                nodes {
                    kind
                    createdAt
                    amount {
                        value
                        }
                    }
                }
            }
        """
        
        payload = {
            "query": query,
            "varibles": varibles
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Api-key': OC_GRAPHQL_KEY
        }
        
        response = requests.post(OC_GRAPHQL_ENDPOINT, json=payload, headers=headers)
        
        response.raise_for_status()
        
        return json.loads(response.content)
    
    def __get_average_cash_flow(period_months: int, data: dict) -> dict[str: int]:
        incoming = 0
        outgoing = 0
        for t in data["data"]["transactions"]["nodes"]:
            value = t["amount"]["value"]
            
            if value > 0:
                incoming += value
            else:
                outgoing += value
                
        return {
            "incoming": round(incoming / period_months, 2),
            "outgoing": round(outgoing / period_months, 2)
        }

    def __get_balance(data: dict) -> int:
        return data["data"]["collective"]["stats"]["balance"]["value"]
    
    def __forecast_negative_cash_date(start_balance: int, cash_flow: int) -> datetime.date:
        months = 0
        while start_balance > 0:
            start_balance += cash_flow
            months += 1

        return date.today() + relativedelta(months=months, day=1)
    
    @classmethod
    def forecast(self) -> dict[str: datetime]:
        time_period = self.__get_data_time_period(OC_ANALYSIS_PERIOD_MONTHS)
        data = self.__get_open_collective_data(time_period)
        cash_flow = self.__get_average_cash_flow(OC_ANALYSIS_PERIOD_MONTHS, data)
        balance = self.__get_balance(data)
        
        return {
            "forecast_no_income": self.__forecast_negative_cash_date(balance, cash_flow["outgoing"]),
            "forecast_continued_income": self.__forecast_negative_cash_date(balance, sum(cash_flow.values()))
        }
    