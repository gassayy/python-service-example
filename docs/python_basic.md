# Python应知应会

## Python基础知识

### 基础数据类型

### For循环

### dataclass

### __metadata__

* Annotated 是 Python 3.9 引入的一个特殊类型构造器，它允许你为类型添加额外的元数据，而不影响实际的类型检查。
```py
from typing import Annotated
from pydantic import BaseModel, Field

# FastAPI/Pydantic 中的使用
class User(BaseModel):
    # 使用 Annotated 添加验证规则
    age: Annotated[int, Field(gt=0, lt=120)]  # 验证年龄在 0-120 之间
    
# 依赖注入中的使用
from fastapi import Query
async def get_items(
    q: Annotated[str | None, Query(min_length=3)] = None
):
    pass
```

### `TYPE_CHECKING` to avoid cicular depedencies

there's a circular import between user_schema.py and models.py:
* `models.py imports from user_schema.py`
* `user_schema.py imports from models.py`
To fix this, we need to break the circular dependency.

*  Move the base models (DbUser and DbUserRole) to a new file, say app/db/base_models.py, 
* Have both models.py and user_schema.py import from there.

Using TYPE_CHECKING is a better solution for breaking circular imports. It's a special constant from the typing module that is False at runtime but True during type checking.
Here's how to properly use it in your models.py:

Only imports during type checking
Avoids circular imports at runtime
Still provides proper type hints for IDE and type checkers
Is more maintainable than creating a separate base models file
The string literal type annotation ("UserIn" instead of UserIn) is used because the actual class isn't available at runtime due to the TYPE_CHECKING condition.

### magic functions


## Pydantic Models


## async function & event loop

### lifespan


## postgres with psycopg

### async connection pool

### raw factories with Pydantic
