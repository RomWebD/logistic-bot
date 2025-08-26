from bot.repositories.base import BaseRepository
from bot.models.google_sheets_binding import GoogleSheetBinding, SheetType, OwnerType
from typing import Optional, List
from sqlalchemy import select, and_, update
from datetime import datetime


class GoogleSheetRepository(BaseRepository[GoogleSheetBinding]):
    
    def __init__(self, session):
        super().__init__(session, GoogleSheetBinding)
    
    async def get_by_telegram_id(self, telegram_id: int) -> List[GoogleSheetBinding]:
        """Отримати всі bindings для telegram_id"""
        result = await self.session.execute(
            select(GoogleSheetBinding).where(
                GoogleSheetBinding.telegram_id == telegram_id
            )
        )
        return list(result.scalars().all())
    
    async def get_by_owner_and_type(
        self, 
        telegram_id: int,
        owner_type: OwnerType,
        sheet_type: SheetType
    ) -> Optional[GoogleSheetBinding]:
        """Знайти binding за власником та типом"""
        result = await self.session.execute(
            select(GoogleSheetBinding).where(
                and_(
                    GoogleSheetBinding.telegram_id == telegram_id,
                    GoogleSheetBinding.owner_type == owner_type,
                    GoogleSheetBinding.sheet_type == sheet_type
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_or_update(
        self,
        telegram_id: int,
        owner_type: OwnerType,
        sheet_type: SheetType,
        sheet_id: str,
        sheet_url: str
    ) -> GoogleSheetBinding:
        """Створити або оновити binding"""
        binding = await self.get_by_owner_and_type(telegram_id, owner_type, sheet_type)
        
        if binding:
            binding.sheet_id = sheet_id
            binding.sheet_url = sheet_url
            binding.updated_at = datetime.utcnow()
        else:
            binding = GoogleSheetBinding(
                telegram_id=telegram_id,
                owner_type=owner_type,
                sheet_type=sheet_type,
                sheet_id=sheet_id,
                sheet_url=sheet_url
            )
            self.session.add(binding)
        
        await self.session.commit()
        await self.session.refresh(binding)
        return binding
    
    async def mark_modified(
        self,
        binding_id: int,
        revision_id: str,
        modified_time: datetime,
        modified_by_email: Optional[str] = None
    ) -> Optional[GoogleSheetBinding]:
        """Позначити як змінений"""
        binding = await self.get_by_id(binding_id)
        if not binding:
            return None
        
        binding.last_revision_id = revision_id
        binding.last_modified_time = modified_time
        binding.last_modified_by_email = modified_by_email
        
        await self.session.commit()
        await self.session.refresh(binding)
        return binding
    
    async def mark_synced(
        self,
        binding_id: int,
        synced_revision: str
    ) -> Optional[GoogleSheetBinding]:
        """Позначити як синхронізований"""
        binding = await self.get_by_id(binding_id)
        if not binding:
            return None
        
        binding.last_synced_at = datetime.utcnow()
        binding.last_synced_revision = synced_revision
        binding.sync_in_progress = False
        
        await self.session.commit()
        await self.session.refresh(binding)
        return binding
    
    async def set_sync_in_progress(self, binding_id: int, in_progress: bool) -> bool:
        """Встановити флаг синхронізації"""
        binding = await self.get_by_id(binding_id)
        if not binding:
            return False
        
        binding.sync_in_progress = in_progress
        await self.session.commit()
        return True
    
    async def get_bindings_needing_sync(self) -> List[GoogleSheetBinding]:
        """Отримати bindings які потребують синхронізації"""
        result = await self.session.execute(
            select(GoogleSheetBinding).where(
                and_(
                    GoogleSheetBinding.sync_in_progress,
                    GoogleSheetBinding.last_revision_id != GoogleSheetBinding.last_synced_revision
                )
            )
        )
        return list(result.scalars().all())