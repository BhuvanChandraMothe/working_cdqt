from urllib.parse import quote_plus
import logging

from testgen.common.database.flavor.flavor_service import FlavorService

LOG = logging.getLogger(__name__)


class MssqlFlavorService(FlavorService):
    def get_connection_string_head(self, strPW):
        username = self.username
        password = quote_plus(strPW)

        strConnect = f"mssql+pyodbc://{username}:{password}@"

        return strConnect

    # def get_connection_string_from_fields(self, strPW, is_password_overwritten: bool = False):    # NOQA ARG002
    #     password = quote_plus(strPW)

    #     strConnect = (
    #         f"mssql+pyodbc://{self.username}:{password}@{self.host}:{self.port}/{self.dbname}?driver=ODBC+Driver+17+for+SQL+Server;"
    #     )

    #     if "synapse" in self.host:
    #         strConnect += "&autocommit=True"
            
    #     LOG.info("Connection string: %s", strConnect)

    #     return strConnect
    

    def get_connection_string_from_fields(self, strPW, is_password_overwritten: bool = False):
        driver_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.dbname};"
            f"UID={self.username};"
            f"PWD={strPW};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )

        connection_string = f"mssql+pyodbc:///?odbc_connect={quote_plus(driver_string)}"
        LOG.info("Connection string: %s", connection_string)
        return connection_string
    
    

    


    def get_pre_connection_queries(self):  # ARG002
        return [
            "SET ANSI_DEFAULTS ON;",
            "SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;",
        ]

    def get_concat_operator(self):
        return "+"
