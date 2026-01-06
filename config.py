from dynaconf import Dynaconf

cfg = Dynaconf(envvar_prefix="DYNACONF",
               settings_files=["config/params.py"])