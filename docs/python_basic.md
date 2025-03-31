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


## References
1. Python 官方文档: https://docs.python.org/
2. FastAPI 文档: https://fastapi.tiangolo.com/
3. Pydantic 文档: https://docs.pydantic.dev/
4. asyncpg 文档: https://magicstack.github.io/asyncpg/
5. Python Type Hints: https://docs.python.org/3/library/typing.html
6. Dataclasses 文档: https://docs.python.org/3/library/dataclasses.html
7. asyncio 文档: https://docs.python.org/3/library/asyncio.html