from dependency_injector import containers, providers

from app.app_layer.services.csv_normalization import CSVService, DataNormalizer


class Container(containers.DeclarativeContainer):
    # app_layer: services
    data_normalizer = providers.Factory(DataNormalizer)
    get_csv_normalization_service = providers.Factory(
        CSVService,
        normalizer=data_normalizer,
    )
