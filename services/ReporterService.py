from helpers.helpers import try_parse_date
from datetime import datetime, timedelta

class ReporterService(object):
    def __init__(self, manager, users):
        self.__manager = manager
        self.__users = users

    def report_simple(self):
        data = self.__manager.data
        result = []
        for user in self.__users.users:
            psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, data)))
            result.append({ "name": self.__users.reportnames[user], "sum": psum })
        return result

    def report(self, arguments):
        rtype = "who"
        total = False
        sort = False
        data = self.__manager.data
        result = []
        start_ts = None
        end_ts = None

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
            for user in self.__users.users:
                psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, data)))
                result.append({"name": self.__users.reportnames[user], "sum": psum})

        if sort:
            result = sorted(result, key=lambda x: x["sum"])
        if total:
            result.append({"name": "Итого", "sum": sum(map(lambda d: d["sum"], result ))})

        return result

    def report_series(self, arguments):
        rtype = "who"
        data = self.__manager.data
        result = []
        start_date = None
        end_date = None
        collapse = False

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
                for user in self.__users.users:
                    psum = sum(map(lambda d: d["price"], filter(lambda d, u = user: d["user"] == u, subdata)))
                    subresult.append({"name": self.__users.reportnames[user], "sum": psum})
            if not collapse or any(el["sum"] != 0 for el in subresult):
                result.append({"date": subdate, "values": subresult})

        return result