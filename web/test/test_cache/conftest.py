# import subprocess

# import pytest
# from xprocess import ProcessStarter


# @pytest.fixture(scope="class")
# def redis_server(xprocess):
#     package_name = "redis"
#     pytest.importorskip(
#         modname=package_name, reason=f"could not find python package {package_name}"
#     )

#     class Starter(ProcessStarter):
#         pattern = "[Rr]eady to accept connections"
#         args = ["redis-server", "--port 6360"]

#         def startup_check(self):
#             out = subprocess.run(
#                 ["redis-cli", "-p", "6360", "ping"], stdout=subprocess.PIPE
#             )
#             return out.stdout == b"PONG\n"

#     xprocess.ensure(package_name, Starter)
#     yield
#     xprocess.getinfo(package_name).terminate()
