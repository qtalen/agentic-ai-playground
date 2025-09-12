from pathlib import Path
import inspect

def get_project_root() -> Path:
    """
    获得项目的根目录，即存放pyproject.toml的那个目录
    :return:
    """
    current_path = Path(__file__).resolve()

    for parent in [current_path, *current_path.parents]:
        if Path(parent / "pyproject.toml").exists():
            return parent

    raise FileNotFoundError("I can not locate the root path through .git")

def get_current_directory() -> Path:
    """
    获得当前调用这个方法的那个py文件所在的目录
    :return:
    """
    current_frame = inspect.currentframe()
    if current_frame is None:
        raise ValueError("Can not locate current frame")

    caller_frame = current_frame.f_back
    if caller_frame is None:
        raise ValueError("Can not locate caller frame")

    caller_file = caller_frame.f_code.co_filename
    return Path(caller_file).resolve().parent