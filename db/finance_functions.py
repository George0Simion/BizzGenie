# # /db/finance_functions.py
# from typing import List, Dict
# import datetime
# from pymongo import MongoClient

# def get_db_client() -> MongoClient:
#     # TODO: read URI from env/config
#     # Example: mongodb://user:pass@localhost:27017
#     uri = "mongodb://localhost:27017"
#     return MongoClient(uri)


# def get_db():
#     client = get_db_client()
#     # choose your DB name here
#     return client["restaurant"]


# def get_daily_profit(start_date: datetime.date,
#                      end_date: datetime.date) -> List[Dict]:
#     """
#     Returns list of {"date": date, "revenue": float, "cost": float, "profit": float}
#     from MongoDB `daily_financials` collection.
#     """
#     db = get_db()
#     coll = db["daily_financials"]

#     # Convert python date to datetime with time; assume UTC midnight
#     start_dt = datetime.datetime.combine(start_date, datetime.time.min)
#     end_dt = datetime.datetime.combine(end_date, datetime.time.max)

#     pipeline = [
#         {
#             "$match": {
#                 "date": {"$gte": start_dt, "$lte": end_dt}
#             }
#         },
#         {
#             # In case you ever have multiple docs per day, we still group & sum
#             "$group": {
#                 "_id": "$date",
#                 "revenue": {"$sum": "$revenue"},
#                 "cost": {"$sum": "$cost"},
#                 "profit": {"$sum": "$profit"},
#             }
#         },
#         {
#             "$sort": {"_id": 1}
#         }
#     ]

#     rows = list(coll.aggregate(pipeline))

#     return [
#         {
#             "date": r["_id"].date(),  # convert datetime -> date
#             "revenue": float(r.get("revenue", 0.0)),
#             "cost": float(r.get("cost", 0.0)),
#             "profit": float(r.get("profit", 0.0)),
#         }
#         for r in rows
#     ]


# def get_profit_by_product(start_date: datetime.date,
#                           end_date: datetime.date,
#                           top_n: int = 20) -> List[Dict]:
#     """
#     Returns top products for a given period, sorted by profit descending.

#     Requires `product_financials` documents with:
#     - date, product_id, product_name, revenue, cost, profit
#     """
#     db = get_db()
#     coll = db["product_financials"]

#     start_dt = datetime.datetime.combine(start_date, datetime.time.min)
#     end_dt = datetime.datetime.combine(end_date, datetime.time.max)

#     pipeline = [
#         {
#             "$match": {
#                 "date": {"$gte": start_dt, "$lte": end_dt}
#             }
#         },
#         {
#             "$group": {
#                 "_id": {
#                     "product_id": "$product_id",
#                     "product_name": "$product_name",
#                 },
#                 "revenue": {"$sum": "$revenue"},
#                 "cost": {"$sum": "$cost"},
#                 "profit": {"$sum": "$profit"},
#             }
#         },
#         {
#             "$sort": {"profit": -1}
#         },
#         {
#             "$limit": top_n
#         }
#     ]

#     rows = list(coll.aggregate(pipeline))

#     return [
#         {
#             "product_id": r["_id"]["product_id"],
#             "product_name": r["_id"]["product_name"],
#             "revenue": float(r.get("revenue", 0.0)),
#             "cost": float(r.get("cost", 0.0)),
#             "profit": float(r.get("profit", 0.0)),
#         }
#         for r in rows
#     ]


# def get_profit_by_product_delta(
#     start_start: datetime.date, start_end: datetime.date,
#     end_start: datetime.date, end_end: datetime.date,
#     top_n: int = 20
# ) -> List[Dict]:
#     """
#     Compare two periods (e.g. last month vs previous month)
#     and return products sorted by profit_delta (end - start).

#     We aggregate twice (period1 & period2) then merge in Python.
#     """
#     db = get_db()
#     coll = db["product_financials"]

#     def aggregate_period(s: datetime.date, e: datetime.date) -> Dict[str, float]:
#         s_dt = datetime.datetime.combine(s, datetime.time.min)
#         e_dt = datetime.datetime.combine(e, datetime.time.max)

#         pipeline = [
#             {
#                 "$match": {
#                     "date": {"$gte": s_dt, "$lte": e_dt}
#                 }
#             },
#             {
#                 "$group": {
#                     "_id": {
#                         "product_id": "$product_id",
#                         "product_name": "$product_name",
#                     },
#                     "profit": {"$sum": "$profit"},
#                 }
#             }
#         ]
#         res = list(coll.aggregate(pipeline))
#         # Map key -> {name, profit}
#         out = {}
#         for r in res:
#             pid = r["_id"]["product_id"]
#             name = r["_id"]["product_name"]
#             out[pid] = {"product_id": pid, "product_name": name, "profit": float(r["profit"])}
#         return out

#     p1 = aggregate_period(start_start, start_end)
#     p2 = aggregate_period(end_start, end_end)

#     # Merge keys from both periods
#     all_pids = set(p1.keys()) | set(p2.keys())
#     rows = []
#     for pid in all_pids:
#         name = (p2.get(pid) or p1.get(pid))["product_name"]
#         profit1 = p1.get(pid, {}).get("profit", 0.0)
#         profit2 = p2.get(pid, {}).get("profit", 0.0)
#         delta = profit2 - profit1
#         rows.append({
#             "product_id": pid,
#             "product_name": name,
#             "profit_period1": profit1,
#             "profit_period2": profit2,
#             "profit_delta": delta,
#         })

#     # Sort by most negative delta first
#     rows.sort(key=lambda r: r["profit_delta"])
#     return rows[:top_n]

# /db/finance_functions.py
"""
For now we use ONLY the mock DB implementation (in-memory fake data),
so tests and agents do not need a real Mongo instance running.

Later, when you have real Mongo, you can switch this file to select
between mock and real implementations based on an environment variable.
"""

import datetime
from typing import List, Dict

from db.mockDB import (
    get_daily_profit as _mock_get_daily_profit,
    get_profit_by_product as _mock_get_profit_by_product,
    get_profit_by_product_delta as _mock_get_profit_by_product_delta,
)

# Re-export the functions with the same signatures

def get_daily_profit(start_date: datetime.date,
                     end_date: datetime.date) -> List[Dict]:
    return _mock_get_daily_profit(start_date, end_date)


def get_profit_by_product(start_date: datetime.date,
                          end_date: datetime.date,
                          top_n: int = 20) -> List[Dict]:
    return _mock_get_profit_by_product(start_date, end_date, top_n)


def get_profit_by_product_delta(
    start_start: datetime.date, start_end: datetime.date,
    end_start: datetime.date, end_end: datetime.date,
    top_n: int = 20,
) -> List[Dict]:
    return _mock_get_profit_by_product_delta(
        start_start, start_end, end_start, end_end, top_n
    )
