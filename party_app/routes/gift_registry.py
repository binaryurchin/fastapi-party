from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlmodel import select, Session

from party_app.dependency import Templates, get_session
from party_app.models import Gift, Party, GiftForm

router = APIRouter(prefix="/party/{party_id}/gifts", tags=["gifts"])


@router.get("/", name="gift_registry_page", response_class=HTMLResponse)
def gift_registry_page(
        request: Request,
        party_id: UUID,
        templates: Templates,
        session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)
    # FIXME: Do we really need this ? We have party.gifts
    gifts = session.exec(select(Gift).where(Gift.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/page_gift_registry.html",
        context={"party": party, "gifts": gifts},
    )

# Endpoint returns a form for editing a gift. This URL includes two parameters: party_id and gift_id.
# gift_id allows us to obtain gift details and prefill the edit form
@router.get("/{gift_id}/edit", name="gift_update_partial", response_class=HTMLResponse)
def gift_update_partial(
        party_id: UUID,
        gift_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)
    if not gift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found")
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_update.html",
        context={"gift": gift, "party_id": party_id},
    )


# Endpoint processes the form data and updates the gift
# gift_id from the URL parameter is used to obtain the correct gift object
@router.put("/{gift_id}/edit", name="gift_update_save_partial", response_class=HTMLResponse)
def gift_update_save_partial(
        party_id: UUID,
        gift_id: UUID,
        gift_form: Annotated[GiftForm, Form()],
        templates: Templates,
        request: Request,
        session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)
    gift = session.get(Gift, gift_id)

    if not gift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found")
    gift.gift_name = gift_form.gift_name
    gift.price = gift_form.price
    gift.link = gift_form.link

    session.add(gift)
    session.commit()
    session.refresh(gift)
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_detail.html",
        context={"gift": gift, "party": party, }
    )

@router.delete("/{gift_id}/delete", name="gift_remove_partial", response_class=HTMLResponse)
def gift_delete_partial(
        gift_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)
    if not gift:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found")
    session.delete(gift)
    session.commit()
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_removed.html",
        context={"gift": gift}
    )

@router.get("/new", name="gift_create_partial", response_class=HTMLResponse)
def gift_create_partial(
        party_id: UUID,
        request: Request,
        templates: Templates,
):
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_create.html",
        context={"party_id": party_id},
    )

@router.post("/new", name="gift_create_save_partial", response_class=HTMLResponse)
def gift_create_save_partial(
        party_id: UUID,
        request: Request,
        templates: Templates,
        gift_form: Annotated[GiftForm, Form()],
        session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
    gift = Gift(
        gift_name=gift_form.gift_name,
        price=gift_form.price,
        link=gift_form.link,
        party_id=party_id
    )
    session.add(gift)
    session.commit()
    session.refresh(gift)
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_detail.html",
        context={"gift": gift, "party": party, }
    )

# Endpoint returns details about a single gift. This URL includes two parameters:
# party_id and gift_id. gift_id is used to obtain gift details and pass them to the template.
# This endpoint is used when the user clicks the "Cancel" button
@router.get("/{gift_id}", name="gift_detail_partial", response_class=HTMLResponse)
def gift_detail_partial(
        party_id: UUID,
        gift_id: UUID,
        request: Request,
        templates: Templates,
        session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)
    party = session.get(Party, party_id)
    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_detail.html",
        context={"party": party, "gift": gift},
    )