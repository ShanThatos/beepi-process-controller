from dotenv import dotenv_values

import utils

ENV = dotenv_values()

SECRET_KEY: str = utils.assert_not_none(ENV["SECRET_KEY"])

PCR_USERNAME: str = utils.assert_not_none(ENV["PCR_USERNAME"])
PCR_PASSWORD: str = utils.assert_not_none(ENV["PCR_PASSWORD"])

PROJECTS_DIR: str = utils.assert_not_none(ENV["PROJECTS_DIR"])

RESTART_CMD: str = utils.assert_not_none(ENV["RESTART_CMD"])