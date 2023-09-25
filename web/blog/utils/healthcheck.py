import os
import time


from blog.core.crud import CRUDBase, Base


def cpu_util():
    with os.popen("cat /proc/stat", "r") as f:
        stat1 = f.readline().split(" ")[2:]
    data = []
    for val in stat1:
        data.append(int(val))
    return sum(data), data[3]


def cpu_temp():
    with os.popen("vcgencmd measure_temp") as f:
        return f.readline().replace("temp=", "").replace("'C\n", "")


def mem_usage():
    with os.popen("free -m | awk 'NR==2{printf \"%s/%s MB\", $2-$3,$2}'") as f:
        return f.readline()


def disk_usage():
    with os.popen(
        'df -h | awk \'$NF=="/"{printf "%d/%dMB", ($2-$3)*1024,$2*1024}\''
    ) as f:
        return f.readline()


def server_healthcheck(to_db, db):
    """
    TODO
    ----
    - windows support (can refer to psutil)
    - save to database
    """
    total_1, idle_1 = cpu_util()
    time.sleep(1)
    total_2, idle_2 = cpu_util()
    total = int(total_2 - total_1)
    usage = int(int(total_2 - total_1) - int(idle_2 - idle_1))
    usage_rate = str(int(float(usage * 100 / total))) + "%"

    health = {
        "cpu": usage_rate,
        "temp": cpu_temp(),
        "mem": mem_usage(),
        "disk": disk_usage(),
    }

    if to_db:
        basecrud = CRUDBase(ServerHealthModel, db)
        instance = basecrud.execite(
            "create",
            **health
        )
    return health


class ServerHealthModel(Base):
    __tablename__ = "bookmark"
    id = Column(Integer, primary_key=True)
    cpu = Column()
    temp = Column()
    memory = Column()
    disk = Column()
    timestamp = Column(DateTime, default=datetime.utcnow)