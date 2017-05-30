from helpers.helpers import try_parse_date
from datetime import datetime, timedelta
from dateutil import relativedelta

OFFSET_ALIASES = {"this":0, "last":1}

class ReporterService(object):
    def __init__(self, manager, users):
        self._manager = manager
        self._users = users

    def report_simple(self):
        data = self._manager.data
        result = []
        for user in self._users.users:
            psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, data)))
            result.append({ "name": self._users.reportnames[user], "sum": psum })
        return result

    def report(self, arguments):
        rtype = "who"
        total = False
        sort = False
        data = self._manager.data
        result = []
        start_ts = None
        end_ts = None

        if "period" in arguments:
            start_ts, end_ts = self._genPeriod(arguments["period"])
            start_ts = start_ts.timestamp()
            end_ts = end_ts.timestamp()

        if "start" in arguments:
            start_ts = try_parse_date(arguments["start"][0])

        if "end" in arguments:
            end_ts = try_parse_date(arguments["end"][0])
            if end_ts:
                end_ts = (datetime.fromtimestamp(end_ts) + timedelta(days=1)).timestamp()

        if "type" in arguments:
            rtype = arguments["type"][0]

        if "total" in arguments:
            total = True

        if "sort" in arguments:
            sort = True

        if start_ts:
            data = list(filter(lambda d: d["date"] >= start_ts, data))

        if end_ts:
            data = list(filter(lambda d: d["date"] < end_ts, data))

        if rtype == "what":
            categories = set(map(lambda x: x["category"], data))
            for cat in categories:
                psum = sum(map(lambda d: d["price"], filter(lambda d, c = cat: d["category"] == c, data)))
                result.append({"name": cat, "sum": psum})
        else:
            for user in self._users.users:
                psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, data)))
                result.append({"name": self._users.reportnames[user], "sum": psum})

        if sort:
            result = sorted(result, key=lambda x: x["sum"])
        if total:
            result.append({"name": "Итого", "sum": sum(map(lambda d: d["sum"], result ))})

        return result

    def report_series(self, arguments):
        rtype = "who"
        data = self._manager.data
        result = []
        start_date = None
        end_date = None
        collapse = False

        if "period" in arguments:
            start_date, end_date = self._genPeriod(arguments["period"])

        if "start" in arguments:
            start_ts = try_parse_date(arguments["start"][0])
            if start_ts:
                start_date = datetime.fromtimestamp(start_ts)

        if "end" in arguments:
            end_ts = try_parse_date(arguments["end"][0])
            if end_ts:
                end_date = datetime.fromtimestamp(end_ts) + timedelta(days=1)

        if "type" in arguments:
            rtype = arguments["type"][0]

        if "collapse" in arguments:
            collapse = True
        
        timestamps = [x["date"] for x in data]

        if not start_date:
           start_date = datetime.fromtimestamp(min(timestamps)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not end_date:
           end_date = datetime.fromtimestamp(max(timestamps)).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        categories = set(map(lambda x: x["category"], data))

        for n in range(int ((end_date - start_date).days)):
            subdate = start_date + timedelta(n)
            start_ts = subdate.timestamp()
            end_ts = (subdate  + timedelta(days=1)).timestamp()
            subdata = list(filter(lambda d: d["date"] >= start_ts and d["date"] < end_ts, data))
            subresult = []

            if rtype == "what":
                for cat in categories:
                    psum = sum(map(lambda d: d["price"], filter(lambda d, c = cat: d["category"] == c, subdata)))
                    subresult.append({"name": cat, "sum": psum})
            else:
                for user in self._users.users:
                    psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, subdata)))
                    subresult.append({"name": self._users.reportnames[user], "sum": psum})
            if not collapse or any(el["sum"] != 0 for el in subresult):
                result.append({"date": subdate, "values": subresult})

        return result

    def _genPeriod(self, arguments):
        dt = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        start = None
        end = None
        period = None
        offset = 0
        if len(arguments) > 0:
            period = arguments[0].lower()
        if len(arguments) > 1:
            offset = arguments[1].lower()
            if (offset in OFFSET_ALIASES):
                offset = OFFSET_ALIASES[offset]
            else:
                try:
                    offset = abs(int(offset))
                except:
                    offset = 0
        if period == "year":
            start = dt.replace(day=1, month=1) - relativedelta.relativedelta(years=offset) 
            end = start + relativedelta.relativedelta(years=1)
        elif period == "month":
            start = dt.replace(day=1) - relativedelta.relativedelta(months=offset) 
            end = start + relativedelta.relativedelta(months=1)
        else:
            start = dt - timedelta(days=dt.weekday()) - timedelta(days=7*offset) 
            end = start + timedelta(days=7)
            pass
        return start, end