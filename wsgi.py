# 生产环境入口：供 gunicorn / 云平台（Render、Railway、HuggingFace Spaces 等）
# 以 `server:app` 方式加载。本地 `python server.py` 开发依然可用，互不影响。
# 注意：本仓库同时存在 server.py（Flask 应用）与 app/ 包（prompt 逻辑），
# 二者不能同名，否则 `from app import app` 会被解析成 app/ 包而失败。
from server import app as application  # noqa: F401

if __name__ == "__main__":
    application.run()
