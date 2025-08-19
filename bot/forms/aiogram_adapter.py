from __future__ import annotations
from typing import Any, Dict, List, Optional, Type
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import Router, F

from .base import BaseForm, FormField


# ======================= Summary =======================


def build_summary_text(
    data: Dict[str, Any],
    form: BaseForm,
    *,
    hide_empty: bool = False,
) -> str:
    titles = form.field_titles()
    lines: List[str] = []
    for fld in form.fields:
        val = data.get(fld.name)
        if hide_empty and (val is None or val == "" or val == []):
            continue
        icon = form.icons.get(fld.name, "•")
        if isinstance(val, (list, set, tuple)):
            shown = ", ".join(map(str, val)) if val else "—"
        else:
            shown = str(val) if val not in (None, "") else "—"
        lines.append(f"{icon} {titles.get(fld.name, fld.name)}: {shown}")

    text = f"{form.summary_header}\n<pre>{'\n'.join(lines)}</pre>"

    if form.include_progress:
        total = len(form.fields)
        filled = sum(
            1 for fld in form.fields if data.get(fld.name) not in (None, [], "")
        )
        pct = int(100 * filled / total) if total else 100

        # --- вибір кольору ---
        if pct < 30:
            fill_emoji = "🟥"
        elif pct < 70:
            fill_emoji = "🟧"
        else:
            fill_emoji = "🟩"

        empty_emoji = "⬜"

        total_blocks = 10
        filled_blocks = round(total_blocks * pct / 100)
        empty_blocks = total_blocks - filled_blocks
        bar = (fill_emoji * filled_blocks) + (empty_emoji * empty_blocks)

        text += f"\n{bar} {pct}% ({filled}/{total})"

    return text


def build_summary_keyboard(
    prefix: str,
    *,
    save_cb: str = "form_save",
    edit_cb: str = "form_edit_menu",
    cancel_cb: str = "form_cancel",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редагувати", callback_data=f"{prefix}:{edit_cb}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Зберегти", callback_data=f"{prefix}:{save_cb}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скасувати", callback_data=f"{prefix}:{cancel_cb}"
                )
            ],
        ]
    )


# ======================= States =======================


class FormStates(StatesGroup):
    """Базовий клас; реальні стани генеруються динамічно."""

    pass


def make_states_for_form(form: BaseForm) -> Type[StatesGroup]:
    """Динамічно створює StatesGroup із полями форми."""
    attrs = {fld.name: State() for fld in form.fields}
    return type(f"{form.__class__.__name__}States", (StatesGroup,), attrs)


# ======================= Router Wrapper =======================

CURSOR_KEY = "__form_cursor__"  # індекс поточного поля
EDIT_MODE_KEY = "__edit_mode__"  # True, якщо йдемо по черзі редагування
EDIT_QUEUE_KEY = "__edit_queue__"  # черга полів для редагування (list[str])


class FormRouter:
    """
    FormRouter з підтримкою унікального prefix.
    Усі callback-и мають формат: "{prefix}:action".
    """

    def __init__(self, form: BaseForm, prefix: str):
        self.form = form
        self.prefix = prefix
        self.router = Router()
        self.States = make_states_for_form(form)
        self._register_handlers()

    # ---------------- utils ----------------
    def _cb(self, suffix: str) -> str:
        return f"{self.prefix}:{suffix}"

    # ---------------- UI helpers ----------------

    def _select_keyboard(
        self, fld: FormField, selected: Optional[List[str]] = None
    ) -> InlineKeyboardMarkup:
        if fld.kind == "select":
            rows = [
                [
                    InlineKeyboardButton(
                        text=label,
                        callback_data=self._cb(f"opt:{fld.name}:{value}"),
                    )
                ]
                for (value, label) in (fld.options or ())
            ]
            if fld.allow_skip:
                rows.append(
                    [
                        InlineKeyboardButton(
                            text="⏭️ Пропустити",
                            callback_data=self._cb(f"skip:{fld.name}"),
                        )
                    ]
                )
            return InlineKeyboardMarkup(inline_keyboard=rows)

        if fld.kind == "multiselect":
            sel = set(selected or [])
            rows = [
                [
                    InlineKeyboardButton(
                        text=("✅ " if value in sel else "") + label,
                        callback_data=self._cb(f"toggle:{fld.name}:{value}"),
                    )
                ]
                for (value, label) in (fld.options or ())
            ]
            rows.append(
                [
                    InlineKeyboardButton(
                        text="✅ Завершити", callback_data=self._cb(f"done:{fld.name}")
                    )
                ]
            )
            if fld.allow_skip:
                rows.append(
                    [
                        InlineKeyboardButton(
                            text="⏭️ Пропустити",
                            callback_data=self._cb(f"skip:{fld.name}"),
                        )
                    ]
                )
            return InlineKeyboardMarkup(inline_keyboard=rows)

        # text
        if fld.allow_skip:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⏭️ Пропустити",
                            callback_data=self._cb(f"skip:{fld.name}"),
                        )
                    ]
                ]
            )
        return InlineKeyboardMarkup(inline_keyboard=[])

    def _render_edit_menu_kb(self, selected: set[str]) -> InlineKeyboardMarkup:
        titles = self.form.field_titles()
        rows, row = [], []
        for fld in self.form.fields:
            name = fld.name
            checked = "✅ " if name in selected else ""
            btn = InlineKeyboardButton(
                text=checked + titles[name], callback_data=self._cb(f"e_toggle:{name}")
            )
            row.append(btn)
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        rows.append(
            [
                InlineKeyboardButton(
                    text="▶️ Почати редагування", callback_data=self._cb("e_start")
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад до підсумку",
                    callback_data=self._cb("form_back_to_summary"),
                )
            ]
        )
        return InlineKeyboardMarkup(inline_keyboard=rows)

    # ---------------- flow helpers ----------------

    async def _ask(
        self,
        message: Message,
        state: FSMContext,
        fld: FormField,
        *,
        idx: Optional[int] = None,
    ):
        if idx is None:
            idx = next(i for i, f in enumerate(self.form.fields) if f.name == fld.name)
        await state.update_data(**{CURSOR_KEY: idx})
        await state.set_state(getattr(self.States, fld.name))
        if fld.kind in ("select", "multiselect"):
            await message.answer(
                fld.prompt or fld.title, reply_markup=self._select_keyboard(fld)
            )
        else:
            await message.answer(
                fld.prompt or f"Введіть: {fld.title}",
                reply_markup=self._select_keyboard(fld),
            )

    async def _goto_next_or_summary(self, message: Message, state: FSMContext):
        data = await state.get_data()
        cur = int(data.get(CURSOR_KEY, -1))
        for j in range(cur + 1, len(self.form.fields)):
            name = self.form.fields[j].name
            if data.get(name) is None:
                await self._ask(message, state, self.form.fields[j], idx=j)
                return

        text = build_summary_text(data, self.form)
        await message.answer(
            text, reply_markup=build_summary_keyboard(self.prefix), parse_mode="HTML"
        )

    async def _advance_after_answer(
        self, message: Message, state: FSMContext, current_field: str
    ):
        data = await state.get_data()
        if data.get(EDIT_MODE_KEY):
            queue: List[str] = list(data.get(EDIT_QUEUE_KEY) or [])
            if current_field in queue:
                queue.remove(current_field)
                await state.update_data(**{EDIT_QUEUE_KEY: queue})
            if queue:
                next_name = queue[0]
                fld = self.form.field_by_name(next_name)
                await self._ask(message, state, fld)
                return
            await state.update_data(**{EDIT_MODE_KEY: False, EDIT_QUEUE_KEY: []})
            text = build_summary_text(await state.get_data(), self.form)
            await message.answer(
                text,
                reply_markup=build_summary_keyboard(self.prefix),
                parse_mode="HTML",
            )
            return

        await self._goto_next_or_summary(message, state)

    # ---------------- Handlers ----------------
    def _strip_prefix(self, cb_data: str) -> str:
        """
        Прибирає "{prefix}:" на початку callback_data.
        """
        if cb_data.startswith(self.prefix + ":"):
            return cb_data[len(self.prefix) + 1 :]
        return cb_data

    def _register_handlers(self):
        r = self.router

        # START
        @r.callback_query(F.data == self._cb("form_start"))
        async def start(cb: CallbackQuery, state: FSMContext):
            init = {f.name: None for f in self.form.fields}
            init[CURSOR_KEY] = -1
            init[EDIT_MODE_KEY] = False
            init[EDIT_QUEUE_KEY] = []
            await state.update_data(**init)
            await cb.answer()
            await self._ask(cb.message, state, self.form.fields[0], idx=0)

        # TEXT fields
        for fld in self.form.fields:
            if fld.kind == "text":

                @r.message(getattr(self.States, fld.name))
                async def _text_handler(msg: Message, state: FSMContext, _fld=fld):
                    raw = (msg.text or "").strip()
                    val = _fld.normalizer(raw) if _fld.normalizer else raw
                    if _fld.validator:
                        err = _fld.validator(val)
                        if err:
                            await msg.answer(f"⚠️ {err}\nСпробуйте ще раз.")
                            return
                    await state.update_data(**{_fld.name: val})
                    await self._advance_after_answer(msg, state, _fld.name)

        # SELECT (single)
        @r.callback_query(F.data.startswith(self._cb("opt:")))
        async def select_one(cb: CallbackQuery, state: FSMContext):
            payload = self._strip_prefix(cb.data)  # "opt:fld:value"
            _, fld_name, value = payload.split(":", 2)
            await state.update_data(**{fld_name: value})
            await cb.answer()
            await self._advance_after_answer(cb.message, state, fld_name)

        # MULTISELECT toggle
        @r.callback_query(F.data.startswith(self._cb("toggle:")))
        async def toggle_multi(cb: CallbackQuery, state: FSMContext):
            payload = self._strip_prefix(cb.data)  # "toggle:fld:value"
            _, fld_name, value = payload.split(":", 2)
            data = await state.get_data()
            cur = set(data.get(fld_name) or [])
            if value in cur:
                cur.remove(value)
            else:
                cur.add(value)
            await state.update_data(**{fld_name: list(cur)})
            fld = self.form.field_by_name(fld_name)
            await cb.message.edit_reply_markup(
                reply_markup=self._select_keyboard(fld, list(cur))
            )
            await cb.answer()

        # MULTISELECT done
        @r.callback_query(F.data.startswith(self._cb("done:")))
        async def done_multi(cb: CallbackQuery, state: FSMContext):
            payload = self._strip_prefix(cb.data)  # "done:fld"
            _, fld_name = payload.split(":", 1)
            await cb.answer()
            await self._advance_after_answer(cb.message, state, fld_name)

        # SKIP
        @r.callback_query(F.data.startswith(self._cb("skip:")))
        async def skip_field(cb: CallbackQuery, state: FSMContext):
            payload = self._strip_prefix(cb.data)  # "skip:fld"
            _, fld_name = payload.split(":", 1)
            fld = self.form.field_by_name(fld_name)
            empty = "" if fld.kind in ("text", "select") else []
            await state.update_data(**{fld_name: empty})
            await cb.answer("Пропущено")
            await self._advance_after_answer(cb.message, state, fld_name)

        # EDIT MENU
        @r.callback_query(F.data == self._cb("form_edit_menu"))
        async def edit_menu(cb: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            selected = set(data.get(EDIT_QUEUE_KEY) or [])
            kb = self._render_edit_menu_kb(selected)
            await cb.message.edit_text(
                "🔁 Оберіть поле для редагування:", reply_markup=kb
            )
            await cb.answer()

        @r.callback_query(F.data.startswith(self._cb("e_toggle:")))
        async def edit_toggle(cb: CallbackQuery, state: FSMContext):
            payload = self._strip_prefix(cb.data)  # "e_toggle:fld"
            _, name = payload.split(":", 1)
            data = await state.get_data()
            selected = set(data.get(EDIT_QUEUE_KEY) or [])
            if name in selected:
                selected.remove(name)
            else:
                selected.add(name)
            await state.update_data(**{EDIT_QUEUE_KEY: list(selected)})
            await cb.message.edit_reply_markup(
                reply_markup=self._render_edit_menu_kb(selected)
            )
            await cb.answer("Готово")

        @r.callback_query(F.data == self._cb("e_start"))
        async def edit_start(cb: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            queue: List[str] = list(data.get(EDIT_QUEUE_KEY) or [])
            if not queue:
                await cb.answer("Оберіть хоча б одне поле", show_alert=False)
                return
            await state.update_data(**{EDIT_MODE_KEY: True})
            first = queue[0]
            fld = self.form.field_by_name(first)
            await cb.answer()
            await self._ask(cb.message, state, fld)

        @r.callback_query(F.data == self._cb("form_back_to_summary"))
        async def back_to_summary(cb: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            text = build_summary_text(data, self.form)
            await cb.message.edit_text(
                text,
                reply_markup=build_summary_keyboard(self.prefix),
                parse_mode="HTML",
            )
            await cb.answer()

        # SAVE / CANCEL
        @r.callback_query(F.data == self._cb("form_save"))
        async def form_save(cb: CallbackQuery, state: FSMContext):
            data = await state.get_data()
            await self.form.on_submit(data, cb.message)
            await state.clear()
            await cb.message.edit_text("✅ Збережено успішно!")
            await cb.answer()

        @r.callback_query(F.data == self._cb("form_cancel"))
        async def form_cancel(cb: CallbackQuery, state: FSMContext):
            await state.clear()
            await cb.message.edit_text("🚫 Скасовано.")
            await cb.answer()
