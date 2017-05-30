from datetime import datetime
import re

def try_parse_date(d):
        match = re.match("([1-3]?\d)\.([0-1]\d)\.(\d{4})", d, re.I)
        if match:
            groups = match.groups()
            day = int(groups[0])
            month = int(groups[1])
            year = int(groups[2])
            try:
                date = datetime(year, month, day)
                return date.timestamp()
            except ValueError:
                return None

        return None