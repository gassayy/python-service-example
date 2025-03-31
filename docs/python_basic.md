# Python应知应会

## Python基础知识

### 基础数据类型
- **数值类型**: int, float, complex
- **字符串**: str (不可变序列)
- **布尔值**: True, False
- **容器类型**:
  - list: 可变序列 `[1, 2, 3]`
  - tuple: 不可变序列 `(1, 2, 3)`
  - dict: 键值对 `{'key': 'value'}`
  - set: 无序不重复集合 `{1, 2, 3}`

### For循环
- 基本语法: `for item in iterable:`
- 带索引遍历: `for i, item in enumerate(iterable):`
- 字典遍历:
  ```python
  for key in dict:  # 遍历键
  for key, value in dict.items():  # 遍历键值对
  ```
- 列表推导式: `[x for x in range(10) if x % 2 == 0]`

### dataclass
- Python 3.7+ 的特性，用于创建数据类
- 自动生成 `__init__`, `__repr__`, `__eq__` 等方法
- 基本用法:
  ```python
  from dataclasses import dataclass
  
  @dataclass
  class Point:
      x: int
      y: int
  ```
- 支持默认值和字段选项

### `__metadata__`
- 类型注解的元数据
- Annotated 用法示例保持不变
- 常见应用场景:
  - FastAPI 参数验证
  - 依赖注入
  - 自定义验证规则

### TYPE_CHECKING 处理循环依赖
- 使用 `typing.TYPE_CHECKING` 在运行时避免循环导入
- 类型标注使用字符串形式
- 实现示例:
  ```python
  from typing import TYPE_CHECKING
  
  if TYPE_CHECKING:
      from .schemas import UserSchema
  
  class User:
      def get_schema(self) -> "UserSchema":
          pass
  ```

### magic functions
- `__init__`: 构造函数
- `__str__`: 字符串表示
- `__repr__`: 开发者字符串表示
- `__len__`: 长度
- `__getitem__`: 索引访问
- `__call__`: 可调用对象

## async function & event loop
- 异步函数定义: `async def`
- `await` 关键字使用
- 事件循环基础:
  ```python
  import asyncio
  
  async def main():
      await some_async_function()
  
  asyncio.run(main())
  ```

### lifespan
- FastAPI 应用生命周期管理
- 启动和关闭事件处理
- 资源管理示例:
  ```python
  from contextlib import asynccontextmanager
  
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # 启动时执行
      await startup()
      yield
      # 关闭时执行
      await shutdown()
  ```

## postgres with psycopg
- 异步数据库连接
- 连接池管理
- SQL 查询执行

### async connection pool
- 使用 asyncpg 创建连接池
- 连接池配置和管理
- 示例:
  ```python
  from asyncpg import create_pool
  
  pool = await create_pool(
      user='user',
      password='password',
      database='dbname',
      host='localhost',
      min_size=5,      # 池中最小连接数
      max_size=20,     # 池中最大连接数
      timeout=30.0     # 获取连接的超时时间
  )
  ```

### raw factories with Pydantic
在使用原始 SQL 查询时，我们常需要将查询结果转换为 Pydantic 模型。以下是详细的实现方式：

#### 1. 基础模型定义
```python
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
```

#### 2. 工厂模式实现
```python
from typing import List, Dict, Any
import asyncpg

class UserFactory:
    @staticmethod
    def from_row(row: asyncpg.Record) -> UserBase:
        # 将数据库行转换为字典
        data = dict(row)
        # 创建 Pydantic 模型实例
        return UserBase(**data)
    
    @staticmethod
    def from_rows(rows: List[asyncpg.Record]) -> List[UserBase]:
        # 批量转换多行数据
        return [UserFactory.from_row(row) for row in rows]

class DatabaseManager:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def fetch_users(self) -> List[UserBase]:
        async with self.pool.acquire() as conn:
            # 执行原始 SQL 查询
            rows = await conn.fetch("""
                SELECT id, username, email, created_at, updated_at
                FROM users
                WHERE is_active = true
            """)
            # 使用工厂方法转换结果
            return UserFactory.from_rows(rows)

    async def execute_with_fallback(self, query: str):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query)
        except asyncpg.exceptions.PoolTimeout:
            # 可以实现降级策略
            # 1. 返回缓存数据
            # 2. 使用备用数据库
            # 3. 返回部分数据
            pass
```

```
from asyncpg.pool import Pool
from typing import Optional, List
import asyncio

class DatabasePool:
    def __init__(
        self,
        pool: Pool,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.pool = pool
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def execute_with_retry(
        self,
        query: str,
        *args,
        retry_count: int = 0
    ) -> Optional[List[Record]]:
        try:
            async with self.pool.acquire(timeout=self.timeout) as conn:
                return await conn.fetch(query, *args)
        except asyncpg.exceptions.PoolTimeout:
            if retry_count < self.max_retries:
                # 指数退避重试
                await asyncio.sleep(2 ** retry_count)
                return await self.execute_with_retry(
                    query,
                    *args,
                    retry_count=retry_count + 1
                )
            raise  # 重试耗尽后抛出异常

async def robust_database_operation():
    try:
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM users")
            return result
    except asyncpg.exceptions.PoolTimeout:
        # 处理连接池超时
        log.warning("Connection pool timeout")
        return await fallback_operation()
    except asyncpg.exceptions.PostgresError:
        # 处理数据库错误
        log.error("Database error")
        raise
```

## References
1. Python 官方文档: https://docs.python.org/
2. FastAPI 文档: https://fastapi.tiangolo.com/
3. Pydantic 文档: https://docs.pydantic.dev/
4. asyncpg 文档: https://magicstack.github.io/asyncpg/
5. Python Type Hints: https://docs.python.org/3/library/typing.html
6. Dataclasses 文档: https://docs.python.org/3/library/dataclasses.html
7. asyncio 文档: https://docs.python.org/3/library/asyncio.html