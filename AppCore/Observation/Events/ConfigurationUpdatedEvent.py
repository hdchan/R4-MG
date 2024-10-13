from ...Config.Configuration import Configuration
from ..TransmissionProtocol import TransmissionProtocol
class ConfigurationUpdatedEvent(TransmissionProtocol):
      def __init__(self, configuration: Configuration):
            self.configuration = configuration