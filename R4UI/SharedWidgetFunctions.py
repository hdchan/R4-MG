from PySide6.QtWidgets import QSizePolicy

class SharedWidgetFunctions:
    def set_size_policy(self, 
                        horizontal_policy: QSizePolicy = QSizePolicy.Policy.Preferred, 
                        vertical_policy: QSizePolicy = QSizePolicy.Policy.Preferred) -> 'SharedWidgetFunctions':
            self.setSizePolicy(horizontal_policy, vertical_policy)
            return self

    def set_size_policy_uniform(self, policy: QSizePolicy) -> 'SharedWidgetFunctions':
        return self.set_size_policy(policy, policy)