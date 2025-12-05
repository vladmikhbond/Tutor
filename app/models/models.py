
import datetime as dt
from sqlalchemy import ForeignKey, String, DateTime, Integer, Text, LargeBinary, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from ..lectorium.parser import Parser

class Base(DeclarativeBase):
    pass


class Lecture(Base):
    __tablename__ = "lectures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disc_id: Mapped[int] = mapped_column(Integer, ForeignKey("discs.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean)
    modified: Mapped[dt.datetime] = mapped_column(DateTime)
    # nav
    disc: Mapped["Disc"] = relationship(back_populates="lectures")

    
    @property
    def title(self):
        """
        Повертає назву лекції 
        """
        slides = Parser(self.content).parse()
        if slides and len(slides):
            return slides[0].text
        else:
            return "notitle"
    
    @property
    def volume(self):
        """
        Повертає об'єм лекції в символах (коменти не рахуються)
        """
        lines = self.content.splitlines()
        lines = filter(lambda l: not l.startswith("@@"), lines)
        return len("\n".join(lines))
        
class Picture(Base):
    __tablename__ = "pictures"
    title: Mapped[str] = mapped_column(String, primary_key=True)
    disc_id: Mapped[int] = mapped_column(Integer, ForeignKey("discs.id", ondelete="CASCADE"), primary_key=True)
    image: Mapped[bytes] = mapped_column(LargeBinary)
    #  nav
    disc: Mapped["Disc"] = relationship(back_populates="pictures")


class Disc(Base):
    __tablename__ = "discs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, ForeignKey("users.username", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String)
    lang: Mapped[str] = mapped_column(String)
    theme: Mapped[str] = mapped_column(String)
    #  nav
    user: Mapped["Tutor"] = relationship(back_populates="discs")
    lectures: Mapped[list["Lecture"]] = relationship(back_populates="disc", cascade="all, delete-orphan")
    pictures: Mapped[list["Picture"]] = relationship(back_populates="disc", cascade="all, delete-orphan")


class Tutor(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    # nav
    discs: Mapped[list["Disc"]] = relationship(back_populates="user", cascade="all, delete-orphan")
