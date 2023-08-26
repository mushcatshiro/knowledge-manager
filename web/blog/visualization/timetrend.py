import datetime as dt

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator


def datetime_validation(x):
    """
    Helper function to guess the datetime format of a string and validate it

    TODO
    ----
    - support datetime formats transformation

    Args:
    -----
    x: str
        string to be converted to datetime
    """
    datetime_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%H:%M:%S"]
    if ":" in x[0] and "-" in x[0]:
        datetime_format = 0
    elif ":" in x[0]:
        datetime_format = 2
    elif "-" in x[0]:
        datetime_format = 1
    else:
        raise ValueError(f"input {x} is not in datetime format")
    
    for item in x:
        try:
            dt.datetime.strptime(item, datetime_formats[datetime_format])
        except ValueError:
            raise ValueError(f"input {item} is not in datetime format {datetime_format}")
    return x, datetime_format


def plot_time_trend(x, y , title, xlabel, ylabel, **kwargs):
    """
    Plot a time trend of a variable
    Args:
    -----
    x: list
        list of x values
    y: list
        list of y values
    title: str
        title of the plot
    xlabel: str
        x-axis label
    ylabel: str
        y-axis label
    kwargs:
        additional keyword arguments to be passed to plt.plot
    Returns:
    --------
    None
    """
    out_path = kwargs.get("out_path", None)
    show = kwargs.get("show", False)

    datetime_validation(x)
    assert len(x) == len(y), "x and y must have the same length"

    plt.tight_layout()
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(MultipleLocator(2))
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator())  # minor ticks do not work with xkcd

    if out_path:
        plt.savefig(out_path)
    if show:
        plt.show()

plot_time_trend(
    x=["2020-01-01 00:00:00", "2020-01-02 00:00:00", "2020-01-03 00:00:00", "2020-01-04 00:00:00"],
    y=[1, 2, 3, 4],
    title="Time trend",
    xlabel="Date",
    ylabel="Value",
    out_path="time_trend.svg",
    show=True
)