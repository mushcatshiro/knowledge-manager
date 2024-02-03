import datetime
import numpy as np
import matplotlib.pyplot as plt

from .model import BookmarkModel
from blog.core.crud import CRUDBase
from blog import db


def summarize_annual_bookmarklet():
    """
    - mon to sunday frequency
      - time of day
    - topic summary
    - overall trend since inception
    """
    day_of_week = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    # sql_statement = "SELECT timestamp FROM bookmark"
    sql_statement = "SELECT * FROM bookmark ORDER BY timestamp DESC"
    c = CRUDBase(BookmarkModel, db)
    instances = c.safe_execute(operation="custom_query", query=sql_statement)
    dow_instances = map(
        lambda x: int(
            datetime.datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%w"
            )
        ),
        instances,
    )
    dow_instances: np.ndarray = np.asarray(list(dow_instances))
    uniques, counts = np.unique(dow_instances, return_counts=True)
    print(uniques, counts)

    # plt.bar(uniques, counts)
    # plt.yticks([x for x in range(0, max(counts) + 1, 5)])
    # plt.xticks(uniques, [day_of_week[day] for day in uniques], rotation=45)
    # plt.show()

    hourly_instances = map(
        lambda x: int(
            datetime.datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%H"
            )
        ),
        instances,
    )
    hourly_instances: np.ndarray = np.asarray(list(hourly_instances))
    uniques, counts = np.unique(hourly_instances, return_counts=True)
    # reverse the order of the array

    # plt.gca().invert_yaxis()
    # plt.barh(uniques, counts)
    # plt.show()

    daily_instances = map(
        lambda x: int(
            datetime.datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S.%f").strftime(
                "%Y-%m-%d"
            )
        ),
        instances,
    )
    daily_instances: np.ndarray = np.asarray(list(daily_instances))
    uniques, counts = np.unique(daily_instances, return_counts=True)
    # running sum
    counts = np.cumsum(counts)

    plt.plot(uniques, counts)
    plt.show()
