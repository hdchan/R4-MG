from .LocalCardResource import *


class StagedCardResource:
    def __init__(self, local_card_resource: LocalCardResource, production_resource: LocalCardResource):
        self.local_card_resource = local_card_resource
        self.production_resource = production_resource