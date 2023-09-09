from dotenv import dotenv_values

import utils

ENV = dotenv_values()

SECRET_KEY: str = utils.assert_not_none(ENV.get("SECRET_KEY"))

PCR_USERNAME: str = utils.assert_not_none(ENV.get("PCR_USERNAME"))
PCR_PASSWORD: str = utils.assert_not_none(ENV.get("PCR_PASSWORD"))

PROJECTS_DIR: str = utils.assert_not_none(ENV.get("PROJECTS_DIR"))

RESTART_CMD: str = utils.assert_not_none(ENV.get("RESTART_CMD"))

TEMPLATES_AUTO_RELOAD: bool = utils.assert_not_none(ENV.get("TEMPLATES_AUTO_RELOAD", "no")) == "yes"

RUN_CLOUDFLARED: bool = utils.assert_not_none(ENV.get("RUN_CLOUDFLARED", "no")) == "yes"
CLOUDFLARED_DOMAIN: str = utils.assert_not_none(ENV.get("CLOUDFLARED_DOMAIN", "X"))