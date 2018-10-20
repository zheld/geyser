import os

from go_service_compiler import GoServiceCompiler


# build or update service
def BuildService(service, dir=None):
    compiler = None
    print("build service")
    conf = service.srvconfig
    if not dir:
        dir = os.getcwd()
    print("working directory: " + dir)
    if conf.lng == "golang":
        compiler = GoServiceCompiler(service, dir)

    # build service
    compiler.Build(conf)
