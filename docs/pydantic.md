# Pydantic Models
- 数据验证和序列化
- 基本用法:
  ```python
  from pydantic import BaseModel
  
  class User(BaseModel):
      name: str
      age: int
      email: str
  ```
  ### 主要特性说明：

1. **嵌套模型**:
   - 支持模型之间的组合和嵌套
   - 可以使用 List, Dict 等容器类型嵌套
   - 支持 Optional 类型表示可选字段
   - 自动进行递归验证

2. **字段验证器**:
   - Field 类提供基础验证规则（长度、范围等）
   - validator 装饰器支持自定义验证逻辑
   - 支持字段间依赖验证
   - 支持验证前后的数据转换
   - 内置多种验证类型（EmailStr, HttpUrl 等）

3. **模型配置选项**:
   - 通过 model_config 或 Config 类配置模型行为
   - 支持 ORM 模式集成
   - 可自定义序列化和反序列化行为
   - 支持字段别名和额外属性处理
   - JSON schema 自定义

#### 1. 嵌套模型
```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class User(BaseModel):
    name: str
    age: int
    # 嵌套单个模型
    address: Address
    # 嵌套模型列表
    alternate_addresses: List[Address] = []
    # 可选嵌套模型
    temporary_address: Optional[Address] = None
```

#### 2. 字段验证器
```python
from pydantic import BaseModel, Field, validator, EmailStr

class User(BaseModel):
    # 使用 Field 进行基础验证
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., gt=0, lt=150)
    email: EmailStr
    
    # 使用 validator 装饰器进行自定义验证
    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()
    
    # 依赖其他字段的验证
    birth_year: int
    registration_year: int
    
    @validator('registration_year')
    def check_registration_year(cls, v, values):
        if 'birth_year' in values and v < values['birth_year']:
            raise ValueError('registration year cannot be before birth year')
        return v
```

#### 3. 模型配置选项
```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class User(BaseModel):
    model_config = ConfigDict(
        # 允许从 ORM 模型创建
        from_attributes=True,
        # 验证赋值
        validate_assignment=True,
        # JSON schema 额外属性
        json_schema_extra={
            "examples": [
                {
                    "name": "John Doe",
                    "age": 30,
                    "email": "john@example.com"
                }
            ]
        },
        # 允许额外字段
        extra='allow',
        # 使用别名
        populate_by_name=True
    )
    
    name: str
    age: int
    created_at: datetime
    
    class Config:
        # 字段别名映射
        alias_generator = lambda field_name: f"user_{field_name}"
        # 序列化时包含默认值
        include_defaults = True
```

```
# 1. 基本使用
user = User(name="John", age=30, created_at=datetime.now())

# 2. 使用别名
user = User(user_name="John", user_age=30, user_created_at=datetime.now())
# 或者（因为 populate_by_name=True）
user = User(name="John", age=30, created_at=datetime.now())

# 3. 包含额外字段（因为 extra='allow'）
user = User(
    name="John",
    age=30,
    created_at=datetime.now(),
    extra_field="value"  # 不会报错
)

# 4. 从 ORM 对象创建（因为 from_attributes=True）
db_user = UserORMModel(name="John", age=30)
user = User.from_orm(db_user)

# 5. 属性赋值验证（因为 validate_assignment=True）
user.age = "invalid"  # 会抛出验证错误
```




