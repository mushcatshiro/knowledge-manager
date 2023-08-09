"""
the lambda functions are to be replaced by other modules for now they are just
placeholders
"""


search = lambda args: f"searching {args}"
todo = lambda args: f"todo {args}"
sd = lambda args: f"sd {args}"
recommend = lambda args: f"recommend {args}"

cmd_mapping = {
    "search": search,
    "todo": todo,
    "sd": sd,
    "recommend": recommend,
}

def cmd_factory(cmd: str):
    """
    using factory pattern to find the correct function to call
    """
    return cmd_mapping.get(cmd, search)

def process_request(enquiry: str) -> str:
    cmd, *args = enquiry.split(" ")
    func = cmd_factory(cmd)
    return func(enquiry)