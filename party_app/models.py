from datetime import date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Column, String, Text

# Common party model for the Party resource
# Defines shared fields used by both the database and form models.
class PartyBase(SQLModel):
    party_date: date
    party_time: time
    invitation: str = Field(
        sa_column=Column(Text), min_length=10
    )
    venue: str = Field(sa_column=Column(String(100))
    )

# Database model for Party resource
# Inherits from PartyBse and represents the actual table, including relationships
class Party(PartyBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    gifts: List["Gift"] = Relationship(
        back_populates="party",
    ) # Defines ORM relationship: party.gifts returns associated Gift objects
    guests: List["Guest"] = Relationship(
        back_populates="party",
    ) # Defines ORM relationship: party.guests returns associated Guest objects

# Form model for Party resource
# Used by FastAPI to validate and process incoming form data for Party resoure
class PartyForm(PartyBase):
    pass

# A common model for Gift resource
# Contains fields used by both database and form models
class GiftBase(SQLModel):
    gift_name: str = Field(sa_column=Column(String(100)))
    price: Decimal = Field(decimal_places=2, ge=0) # Decimal constraints enforced by Pydantic
    link: Optional[str]
    party_id: UUID = Field(
        default=None,
        foreign_key="party.uuid",
    ) # Defines foreign key connecting the gift to party on database level

# Database model for Gift resource
# Inherits from GiftBase and represents the gift table, including its relationship to Party.
class Gift(GiftBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    party: Party = Relationship(
        back_populates="gifts",
    )

# Form model for the Gift resource
# Used for validating and processing incoming gift data via FasAPI
class GiftForm(GiftBase):
    pass

class GuestBase(SQLModel):
    name: str = Field(sa_column=Column(String(100)))
    attending: bool = False
    party_id: UUID = Field(
        default=None,
        foreign_key="party.uuid",
    )

class Guest(GuestBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    party: Party = Relationship(
        back_populates="guests",
    )

class GuestForm(GuestBase):
    pass