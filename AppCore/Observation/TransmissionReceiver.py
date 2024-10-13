from .TransmissionProtocol import TransmissionProtocol


class TransmissionReceiver:
    def handle_observation_tower_event(self, event: TransmissionProtocol) -> None:
        raise Exception()