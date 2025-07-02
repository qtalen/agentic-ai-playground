import importlib
import sys
from types import ModuleType
from typing import Type, Any

import mlflow


TARGET_MODULE = "mlflow.types.chat"
ORIGINAL_CLASS_NAME = "ChatMessage"
BASE_CLASS = "BaseModel"

mlflow.autogen.autolog()

module = importlib.import_module(TARGET_MODULE)
BaseModel = getattr(module, ORIGINAL_CLASS_NAME)

class ChatMessage(BaseModel):
    role: str
    content: str | list | dict | None = None

class ClassReplacer:
    def __init__(
            self,
            target_module: str = TARGET_MODULE,
            original_class_name: str = ORIGINAL_CLASS_NAME,
            new_class: Type = None,
    ):
        self._target_module = target_module
        self._original_class_name = original_class_name
        self._new_class = new_class

        self._module = importlib.import_module(self._target_module)
        self._original_class = getattr(self._module, original_class_name)

    def apply(self):
        for mod_name, mod in list(sys.modules.items()):
            if mod is None or not isinstance(mod, ModuleType):
                continue

            if hasattr(mod, self._original_class_name):
                current_ref = getattr(mod, self._original_class_name)
                if current_ref is self._original_class:
                    setattr(mod, self._original_class_name, self._new_class)

ClassReplacer(new_class=ChatMessage).apply()