from fastapi import FastAPI
from router.universal_tool.OTA_tool import OTA_tool
from router.universal_tool import OBD_tool
from fastapi.middleware.cors import CORSMiddleware
def setup_routers():
    need_auth_routers = [
        OTA_tool.router,
        OBD_tool.router
    ]
    for route in need_auth_routers:
        app.include_router(route)
# 配置 CORS 中间件
origins = [
    "http://localhost:8080",  # Vue 默认端口
]


app = FastAPI()
setup_routers()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有头部
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    app.run(debug=True)

