from typing import Optional, List
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.repositories.base import BaseRepository
from bot.handlers.client.utils import _now_utc
from bot.models.google_sheets_binding import (
    GoogleSheetBinding,
    SheetType,
    OwnerType,
    SheetStatus,
)


class GoogleSheetRepository(BaseRepository[GoogleSheetBinding]):
    def __init__(self, session):
        super().__init__(session, GoogleSheetBinding)

    async def get_by_telegram_id(self, telegram_id: int) -> List[GoogleSheetBinding]:
        res = await self.session.execute(
            select(GoogleSheetBinding).where(
                GoogleSheetBinding.telegram_id == telegram_id,
            )
        )
        return list(res.scalars().all())

    async def get_by_owner_and_type(
        self, telegram_id: int, owner_type: OwnerType, sheet_type: SheetType
    ) -> Optional[GoogleSheetBinding]:
        res = await self.session.execute(
            select(GoogleSheetBinding).where(
                and_(
                    GoogleSheetBinding.telegram_id == telegram_id,
                    GoogleSheetBinding.owner_type == owner_type,
                    GoogleSheetBinding.sheet_type == sheet_type,
                )
            )
        )
        return res.scalar_one_or_none()

    async def get_ready_binding_by_owner_and_type(
        self, telegram_id: int, owner_type: OwnerType, sheet_type: SheetType
    ) -> Optional[GoogleSheetBinding]:
        res = await self.session.execute(
            select(GoogleSheetBinding).where(
                and_(
                    GoogleSheetBinding.telegram_id == telegram_id,
                    GoogleSheetBinding.owner_type == owner_type,
                    GoogleSheetBinding.sheet_type == sheet_type,
                    GoogleSheetBinding.status == SheetStatus.READY,
                    GoogleSheetBinding.sheet_id.is_not(None),
                    GoogleSheetBinding.sheet_url.is_not(None),
                )
            )
        )
        return res.scalar_one_or_none()

    async def get_or_create(
        self, telegram_id: int, owner_type: OwnerType, sheet_type: SheetType
    ) -> GoogleSheetBinding:
        binding = await self.get_by_owner_and_type(telegram_id, owner_type, sheet_type)
        if not binding:
            binding = GoogleSheetBinding(
                telegram_id=telegram_id,
                owner_type=owner_type,
                sheet_type=sheet_type,
                status=SheetStatus.NONE,
                created_at=_now_utc(),
                updated_at=_now_utc(),
            )
            self.session.add(binding)
            await self.session.commit()
            await self.session.refresh(binding)
        return binding

    async def create_or_update(
        self,
        telegram_id: int,
        owner_type: OwnerType,
        sheet_type: SheetType,
        sheet_id: str,
        sheet_url: str,
    ) -> GoogleSheetBinding:
        binding = await self.get_by_owner_and_type(telegram_id, owner_type, sheet_type)
        now = _now_utc()
        if binding:
            binding.sheet_id = sheet_id
            binding.sheet_url = sheet_url
            binding.updated_at = now
            # якщо таблиця гарантовано існує — можна перевести в READY
            if binding.status in (
                SheetStatus.NONE,
                SheetStatus.CREATING,
                SheetStatus.FAILED,
            ):
                binding.status = SheetStatus.READY
        else:
            binding = GoogleSheetBinding(
                telegram_id=telegram_id,
                owner_type=owner_type,
                sheet_type=sheet_type,
                sheet_id=sheet_id,
                sheet_url=sheet_url,
                status=SheetStatus.READY,
                created_at=now,
                updated_at=now,
            )
            self.session.add(binding)
        await self.session.commit()
        await self.session.refresh(binding)
        return binding

    async def update_status(
        self,
        binding_id: int,
        status: SheetStatus,
        sheet_id: Optional[str] = None,
        sheet_url: Optional[str] = None,
        last_synced_revision: Optional[str] = None,
    ) -> Optional[GoogleSheetBinding]:
        binding = await self.get_by_id(binding_id)
        if not binding:
            return None
        binding.status = status
        if sheet_id is not None:
            binding.sheet_id = sheet_id
        if sheet_url is not None:
            binding.sheet_url = sheet_url
        if last_synced_revision is not None:
            binding.last_synced_revision = last_synced_revision
            binding.last_synced_at = _now_utc()
        binding.updated_at = _now_utc()
        await self.session.commit()
        await self.session.refresh(binding)
        return binding

    # атомарний лок на синк (через статус SYNCING)
    async def acquire_sync_lock(
        self, telegram_id: int, owner_type: OwnerType, sheet_type: SheetType
    ) -> bool:
        stmt = (
            update(GoogleSheetBinding)
            .where(
                and_(
                    GoogleSheetBinding.telegram_id == telegram_id,
                    GoogleSheetBinding.owner_type == owner_type,
                    GoogleSheetBinding.sheet_type == sheet_type,
                    GoogleSheetBinding.status != SheetStatus.SYNCING,
                )
            )
            .values(status=SheetStatus.SYNCING, updated_at=_now_utc())
        )
        res = await self.session.execute(stmt)
        if res.rowcount and res.rowcount > 0:
            await self.session.commit()
            return True
        return False

    async def release_sync_lock(
        self,
        telegram_id: int,
        owner_type: OwnerType,
        sheet_type: SheetType,
        new_status: SheetStatus,
        *,
        sheet_id: Optional[str] = None,
        sheet_url: Optional[str] = None,
        last_synced_revision: Optional[str] = None,
    ) -> None:
        binding = await self.get_by_owner_and_type(telegram_id, owner_type, sheet_type)
        if not binding:
            return
        await self.update_status(
            binding.id,
            new_status,
            sheet_id=sheet_id,
            sheet_url=sheet_url,
            last_synced_revision=last_synced_revision,
        )

    async def mark_modified(
        self,
        binding_id: int,
        revision_id: str,
        modified_time: datetime,
        modified_by_email: Optional[str] = None,
    ) -> Optional[GoogleSheetBinding]:
        binding = await self.get_by_id(binding_id)
        if not binding:
            return None
        binding.last_revision_id = revision_id
        binding.last_modified_time = modified_time
        binding.last_modified_by_email = modified_by_email
        binding.updated_at = _now_utc()
        await self.session.commit()
        await self.session.refresh(binding)
        return binding

    async def mark_synced(
        self, binding_id: int, synced_revision: str
    ) -> Optional[GoogleSheetBinding]:
        binding = await self.get_by_id(binding_id)
        if not binding:
            return None
        binding.last_synced_at = _now_utc()
        binding.last_synced_revision = synced_revision
        binding.updated_at = _now_utc()
        await self.session.commit()
        await self.session.refresh(binding)
        return binding

    async def get_ready_client_request_bindings(self) -> List[GoogleSheetBinding]:
        """
        Для тасок: усі клієнтські 'Заявки' зі статусом READY та валідними id/url.
        """
        res = await self.session.execute(
            select(GoogleSheetBinding).where(
                and_(
                    GoogleSheetBinding.owner_type == OwnerType.CLIENT,
                    GoogleSheetBinding.sheet_type == SheetType.REQUESTS,
                    GoogleSheetBinding.status == SheetStatus.READY,
                    GoogleSheetBinding.sheet_id.is_not(None),
                    GoogleSheetBinding.sheet_url.is_not(None),
                )
            )
        )
        return list(res.scalars().all())
