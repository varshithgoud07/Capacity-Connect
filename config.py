import os



SECRET_KEY = "studentportal123"



DATABASE_URL = os.getenv(

    "DATABASE_URL",

    "postgresql://capacity_connect_user:oZyUBeTi0XoDF0G8GIbyhqRs8xUw0Bn1@dpg-dacj9muq1p3s738cfl6g-a.singapore-postgres.render.com/capacity_connect"

)



DEBUG = True