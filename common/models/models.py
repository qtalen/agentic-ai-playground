from enum import StrEnum


class Qwen3(StrEnum):
    MAX = "qwen3-max"
    PLUS = "qwen-plus-latest"
    FLASH = "qwen-flash"

    NEXT = "qwen3-next-80b-a3b-instruct"
    NEXT_THINKING = "qwen3-next-80b-a3b-thinking"
    Q235B_A22B = "qwen3-235b-a22b-instruct-2507"
    Q235B_A22B_THINKING = "qwen3-235b-a22b-thinking-2507"
    Q30B_A3B = "qwen3-30b-a3b-instruct-2507"
    Q30B_A3B_THINKING = "qwen3-30b-a3b-thinking-2507"
    VL_235B_A22B = "qwen3-vl-235b-a22b-instruct"
    VL_235B_A22B_THINKING = "qwen3-vl-235b-a22b-thinking"
    VL_30B_A3B = "qwen3-vl-30b-a3b-instruct"
    VL_30B_A3B_THINKING = "qwen3-vl-30b-a3b-thinking"


class DeepSeek(StrEnum):
    CHAT = "deepseek-chat"
    REASONER = "deepseek-reasoner"
