from datetime import date
from dateutil.relativedelta import relativedelta
from constants import OC_GRAPHQL_ENDPOINT, OC_GRAPHQL_KEY, OC_ANALYSIS_PERIOD_MONTHS
import requests
import json

class OpenCollective:
    """"""


    def __get_open_collective_data(period_months: int) -> dict:
        # TODO
        # Adjustable date
        
        query = """
        query {
            collective(slug: "twohoursonelife") {
                stats {
                    balance {
                        value
                    }
                }
            }
            transactions(
                account: [{ slug: "twohoursonelife" }]
                dateFrom: "2022-07-01T00:00:00Z"
                dateTo: "2022-12-31T23:59:59Z"
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
        
        headers = {
            'Content-Type': 'application/json',
            'Api-key': OC_GRAPHQL_KEY
        }
        
        response = requests.post(OC_GRAPHQL_ENDPOINT,
                                 json={'query': query}, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Open Collective GraphQL query failed, returning {response.status_code} {query}")
        
        return json.loads(response.content)
    
    def __get_average_cash_flow(period_months: int, data: dict) -> dict:
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
    
    def __forecast_negative_cash_date(start_balance: int, cash_flow: int) -> int:
        months = 0
        while start_balance > 0:
            start_balance += cash_flow
            months += 1

        return (date.today() + relativedelta(months=+months))#.strftime("%B")
    
    @classmethod
    def forecast(self):
        data = self.__get_open_collective_data(OC_ANALYSIS_PERIOD_MONTHS)
        cash_flow = self.__get_average_cash_flow(OC_ANALYSIS_PERIOD_MONTHS, data)
        balance = self.__get_balance(data)
        
        return {
            "no_income": self.__forecast_negative_cash_date(balance, cash_flow["outgoing"]),
            "forecast_income": self.__forecast_negative_cash_date(balance, sum(cash_flow.values()))
        }
    