from src import env_vars
from src.common.handler import PlatformFactory


class MuestrasServiceFactory(PlatformFactory):

    def build(self):
        from src.services.Redlie import MuestrasService
        from src.repositories.s3_repository import S3Repository
        from src.repositories.pgsql_repository import PgsqlRepository
        from src.domain import imports
        from src.domain import vocablos

        _service = MuestrasService(
            database=self.database,
            repository=PgsqlRepository(),
            s3_repository=S3Repository(env_vars.S3_BUCKET),
            event_bus=self.events,
            logger=self.lambda_logs,
            metrics=self.metrics,
            tracer=self.tracer,
        )
        _service.csv_document = imports
        _service.vocablos = vocablos
        return _service
