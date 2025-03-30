"""Pydantic models overriding base DbUser fields."""

from typing import Annotated, Optional

from pydantic import AwareDatetime, BaseModel, Field

from app.db.enums import ProjectRole, UserRole
from app.db.models import DbUser, DbUserRole
from app.db.utils import PaginationInfo


class UserIn(DbUser):
    """User details for insert into DB."""

    # Only id and username are mandatory
    # NOTE this is a unique case where the primary key is not auto-generated
    # NOTE we use the OSM ID in most cases, which is unique from OSM
    pass


class UserUpdate(DbUser):
    """User details for update in DB."""

    # Exclude (do not allow update)
    id: Annotated[Optional[int], Field(exclude=True)] = None
    username: Annotated[Optional[str], Field(exclude=True)] = None
    registered_at: Annotated[Optional[AwareDatetime], Field(exclude=True)] = None
    tasks_mapped: Annotated[Optional[int], Field(exclude=True)] = None
    tasks_validated: Annotated[Optional[int], Field(exclude=True)] = None
    tasks_invalidated: Annotated[Optional[int], Field(exclude=True)] = None
    project_roles: Annotated[Optional[dict[int, ProjectRole]], Field(exclude=True)] = (
        None
    )
    orgs_managed: Annotated[Optional[list[int]], Field(exclude=True)] = None


class UserOut(DbUser):
    """User with ID and role."""

    # Mandatory user role field
    role: UserRole


class UserRole(BaseModel):
    """User role only."""

    role: UserRole


# Models for DbUserRole


class UserRolesOut(DbUserRole):
    """User role for a specific project."""

    user_id: int
    role: ProjectRole
    project_id: Optional[int] = None


class PaginatedUsers(BaseModel):
    """Project summaries + Pagination info."""

    results: list[UserOut]
    pagination: PaginationInfo


class Usernames(BaseModel):
    """User info with username and their id."""

    id: int
    username: str