from datetime import datetime
from enum import Enum

class StringFormatter:
    class Duration(Enum):
        SECONDS = 60
        MINUTES = 60
        HOURS = 24
        DAYS = 7

    def format_date(self, dt: datetime) -> str:
        # now = datetime.now()
        # diff_seconds = (now - dt).total_seconds()
        
        
        # counter = 0
        # #            m,  h,  d, w
        # durations = [60, 60, 24, 7]
        # div = 1
        # for d in durations:
        #     if diff_seconds / (div * d) < 1:
        #         break
        #     # if diff_seconds / div < 1:
        #     #     break
        #     div *= d
        #     counter += 1
            

        # duration_result = int(diff_seconds//div)
        # # result = ""
        # if counter == 0:
        #     return f'<{duration_result}1min ago'
        # elif counter == 1:
        #     return f'{duration_result}min ago'
        # elif counter == 2:
        #     return f'{duration_result}hr ago'
        # elif counter == 3:
        #     return f'{duration_result}d ago'
        # else:
        #     return "A long time ago..."
        return dt.strftime("%m/%d/%Y, %I:%M %p")