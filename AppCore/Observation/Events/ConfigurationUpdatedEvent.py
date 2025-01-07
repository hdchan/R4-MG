from ...Config.Configuration import Configuration
from ..TransmissionProtocol import TransmissionProtocol


class ConfigurationUpdatedEvent(TransmissionProtocol):
      def __init__(self, configuration: Configuration, old_configuration: Configuration):
            self.configuration = configuration
            self.old_configuration = old_configuration