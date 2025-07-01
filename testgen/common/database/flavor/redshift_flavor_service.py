from urllib.parse import quote_plus
import logging

from testgen.common.database.flavor.flavor_service import FlavorService

LOG = logging.getLogger("testgen")

class RedshiftFlavorService(FlavorService):
    LOG.info("the flavor is {self.flavor}")
    def get_connection_string_head(self, strPW):
        LOG.info("the flavor is {self.flavor}")
        strConnect = f"postgresql://{self.username}:{quote_plus(strPW)}@"
        return strConnect

    def get_connection_string_from_fields(self, strPW, is_password_overwritten: bool = False):  # NOQA ARG002
        # STANDARD FORMAT:  strConnect = 'flavor://username:password@host:port/database'
        LOG.info("the flavor is {self.flavor}")
        strConnect = f"postgresql://{self.username}:{quote_plus(strPW)}@{self.host}:{self.port}/{self.dbname}"
        return strConnect

    def get_pre_connection_queries(self):
        return [
            "SET SEARCH_PATH = '" + self.dbschema + "'",
        ]

    def get_connect_args(self, is_password_overwritten: bool = False):  # NOQA ARG002
        return {}
