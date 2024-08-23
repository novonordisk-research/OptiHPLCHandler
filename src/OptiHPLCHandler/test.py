from OptiHPLCHandler import EmpowerHandler

with EmpowerHandler(
    project="Mobile",
    auto_login=False,
    username="jxow",
    address="https://reappnnit024n.corp.novocorp.net:3076",
) as empowerHandler:
    empowerHandler.connection.default_post_timeout = 120
    empowerHandler.connection.default_get_timeout = 120
    empowerHandler.login(username="jxow", password="jian xiong wu8")
    projects = empowerHandler.GetEmpowerProjects()
    for project in projects:
        print(project)
