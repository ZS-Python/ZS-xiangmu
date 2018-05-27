from flask import Blueprint

passport_blue = Blueprint('passport',__name__,url_prefix='/passport')  # passport文件夹中的视图都在/passport路径下

from . import views