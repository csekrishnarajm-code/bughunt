from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import clock
from .db import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    language: Mapped[str] = mapped_column(String(12))
    total: Mapped[int] = mapped_column(Integer)
    challenge_ids: Mapped[list] = mapped_column(JSON)
    position: Mapped[int] = mapped_column(Integer, default=0)          # challenges answered so far
    question_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)    # for the current challenge
    score: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=clock.now)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    answers: Mapped[list["Answer"]] = relationship(back_populates="game", order_by="Answer.id")

    @property
    def finished(self) -> bool:
        return self.position >= self.total


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), index=True)
    challenge_id: Mapped[str] = mapped_column(String(40))
    language: Mapped[str] = mapped_column(String(12))
    difficulty: Mapped[str] = mapped_column(String(8))
    category: Mapped[str] = mapped_column(String(60))
    outcome: Mapped[str] = mapped_column(String(8))                    # correct | wrong | timeout
    points: Mapped[int] = mapped_column(Integer)
    time_ms: Mapped[int] = mapped_column(Integer)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)

    game: Mapped[Game] = relationship(back_populates="answers")
