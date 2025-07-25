from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from party_app.dependency import Templates, get_session
from party_app.models import Guest, Party

router = APIRouter(prefix="/party/{party_id}/guests", tags=["guests"])

@router.get("/", name="guest_list_page", response_class=HTMLResponse)
def guest_list_page(
        party_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
):
    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/page_guest_list.html",
        context={"guests": guests, "party_id": party_id}
    )

@router.put("/mark-attending", name="mark_guests_attending_partial", response_class=HTMLResponse)
def mark_guests_attending_partial(
        party_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
        guest_ids: list[UUID] = Form(...)
):
    attending_guests = session.exec(select(Guest).where(Guest.uuid.in_(guest_ids))).all()
    for guest in attending_guests:
        guest.attending = True
    session.commit()

    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_list.html",
        context={"guests": guests}
    )

@router.put("/mark-non-attending", name="mark_guests_not_attending_partial", response_class=HTMLResponse)
def mark_guests_not_attending_partial(
        party_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
        guest_ids: list[UUID] = Form(...)
):
    not_attending_guests = session.exec(select(Guest).where(Guest.uuid.in_(guest_ids))).all()
    for guest in not_attending_guests:
        guest.attending = False
    session.commit()

    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_list.html",
        context={"guests": guests}
    )

@router.post("/filter", name="filter_guests_partial", response_class=HTMLResponse)
def filter_guests_partial(
        party_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
        guest_search: str = Form(...),
):
    guests = session.exec(select(Guest).where((Guest.party_id == party_id) & (Guest.name.ilike(f"%{guest_search}%")))).all()
    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_list.html",
        context={"guests": guests, "party_id": party_id}
    )