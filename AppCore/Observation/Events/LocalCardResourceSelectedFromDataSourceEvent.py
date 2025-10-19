from AppCore.Models import LocalCardResource, DataSourceSelectedLocalCardResourceProtocol

from ..TransmissionProtocol import TransmissionProtocol


class LocalCardResourceSelectedFromDataSourceEvent(TransmissionProtocol):
    def __init__(self,
                 local_resource: LocalCardResource, 
                 data_source: DataSourceSelectedLocalCardResourceProtocol):
        self.local_resource = local_resource
        self.datasource = data_source