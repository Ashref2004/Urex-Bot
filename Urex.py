import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import (

    Updater,

    CommandHandler,

    MessageHandler,

    CallbackContext,

    ConversationHandler,

    CallbackQueryHandler,

    PicklePersistence,

    filters

)

from datetime import datetime, timedelta

import os

import re

import pytz

from typing import Dict, List, Tuple, Optional

from enum import Enum, auto

import random



logging.basicConfig(

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    level=logging.INFO,

    handlers=[

        logging.FileHandler("urex_bot.log"),

        logging.StreamHandler()

    ]

)

logger = logging.getLogger(__name__)



class State(Enum):

    LOGIN_ID = auto()

    LOGIN_PASSWORD = auto()

    AUTHENTICATED = auto()

    ADMIN_PANEL = auto()

    EVENT_MANAGEMENT = auto()

    ADD_EVENT = auto()

    EDIT_EVENT = auto()

    REMOVE_EVENT = auto()

    ANNOUNCEMENT_MANAGEMENT = auto()

    ADD_ANNOUNCEMENT = auto()

    USER_MANAGEMENT = auto()

    FEEDBACK = auto()



class Role(Enum):

    ADMIN = "admin"

    MODERATOR = "moderator"

    MEMBER = "member"

    GUEST = "guest"



class EventStatus(Enum):

    UPCOMING = "قريب"

    ONGOING = "جاري"

    COMPLETED = "منتهي"

    CANCELED = "ملغى"



class Database:

    def __init__(self):

        self.users = {

            "Achref": {

                "password": "27-10-2004", 

                "role": Role.ADMIN.value,

                "full_name": "أشرف مهلول",

                "phone": "+213782675199",

                "join_date": "2025-03-01"

            },

            "AbdElGhani": {

                "password": "30-05-2003", 

                "role": Role.ADMIN.value,

                "full_name": "جودي عبد الغاني",

                "phone": "+21392434376",

                "join_date": "2023-09-01"

            },

            "Omar": {

                "password": "OMAR", 

                "role": Role.MODERATOR.value,

                "full_name": "بومدين عمار",

                "phone": "+213671738833",

                "join_date": "2023-09-10"

            },

            "Amine": {

                "password": "14-11-2004", 

                "role": Role.MODERATOR.value,

                "full_name": "أمين داشير",

                "phone": "+213657512004",

                "join_date": "2023-10-01"

            },

            "Akram": {

                "password": "23-07-2004", 

                "role": Role.MEMBER.value,

                "full_name": "غانس أكرم",

                "phone": "+21379312394",

                "join_date": "2024-11-01"

            },

            "Ayoube": {

                "password": "26-02-2005", 

                "role": Role.MEMBER.value,

                "full_name": "العاني أيوب",

                "phone": "+213676421163",

                "join_date": "2025-04-15"

            },

            "guest": {

                "password": "Urex",

                "role": Role.GUEST.value,

            }

        }

        

        self.events = {

            "1": {

                "title": "دورة حول الأردوينو",

                "description": "يقدم لكم السيد أمين داشير مفاهيم حول عمل الأردوينو وأهميته وكيفية كسب المال منه وشرح حول أهمية القطع الخاصة به وكيفية تركيبها",

                "date": "2025-05-01",

                "time": "14:00",

                "duration": "3 ساعات",

                "location": "القاعة A104",

                "speaker": "ط.أمين داشير",

                "capacity": 30,

                "registered": ["Achref", "Amine"],

                "status": EventStatus.UPCOMING.value,

                "created_at": "2025-03-01",

                "image": None

            },

            "2": {

                "title": "جلسة حول أهمية تحصين النفس",

                "description": "جلسة مناقشة وتوعية عن العالم الأخر وسلبياته وإيجابياته في عالم الإنس وكيفية تحصين النفس",

                "date": "2025-05-02",

                "time": "14:00",

                "duration": "2 ساعات",

                "location": "مكتب النادي",

                "speaker": "ط.مهلول أشرف",

                "capacity": 20,

                "registered": ["Achref", "ElRodji", "Ayoube"],

                "status": EventStatus.UPCOMING.value,

                "created_at": "2025-05-02",

                "image": None

            }

        }

        

        self.announcements = [

            {

                "id": 1,

                "title": "اجتماع عام للنادي",

                "content": "سيتم عقد اجتماع عام لجميع أعضاء النادي يوم الإثنين لمناقشة خطة الفصل القادم",

                "date": "2025-04-28",

                "priority": "high",

                "pinned": True

            },

            {

                "id": 2,

                "title": "الحدث الأخير",

                "content": "إجتماع حول الحدث الأخير",

                "date": "2025-05-05",

                "priority": "medium",

                "pinned": False

            }

        ]

        

        self.feedback = []

        self.statistics = {

            "total_users": 6,

            "active_users": 4,

            "total_events": 2,

            "upcoming_events": 2,

            "announcements_count": 2

        }



    def add_event(self, event_data: Dict) -> str:

        new_id = str(max([int(k) for k in self.events.keys()] + [0]) + 1)

        event_data.update({

            "registered": [],

            "status": EventStatus.UPCOMING.value,

            "created_at": datetime.now().strftime("%Y-%m-%d")

        })

        self.events[new_id] = event_data

        self.statistics["total_events"] += 1

        self.statistics["upcoming_events"] += 1

        return new_id



    def remove_event(self, event_id: str) -> bool:

        if event_id in self.events:

            if self.events[event_id]["status"] == EventStatus.UPCOMING.value:

                self.statistics["upcoming_events"] -= 1

            self.statistics["total_events"] -= 1

            del self.events[event_id]

            return True

        return False



    def update_event(self, event_id: str, updates: Dict) -> bool:

        if event_id in self.events:

            old_status = self.events[event_id].get("status")

            self.events[event_id].update(updates)

            

            if "status" in updates:

                new_status = updates["status"]

                if old_status == EventStatus.UPCOMING.value and new_status != EventStatus.UPCOMING.value:

                    self.statistics["upcoming_events"] -= 1

                elif old_status != EventStatus.UPCOMING.value and new_status == EventStatus.UPCOMING.value:

                    self.statistics["upcoming_events"] += 1

            

            return True

        return False



    def add_announcement(self, announcement_data: Dict) -> int:

        new_id = max([a["id"] for a in self.announcements] + [0]) + 1

        announcement_data["id"] = new_id

        announcement_data["date"] = datetime.now().strftime("%Y-%m-%d")

        self.announcements.append(announcement_data)

        self.statistics["announcements_count"] += 1

        return new_id



    def add_feedback(self, feedback_data: Dict) -> None:

        feedback_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.feedback.append(feedback_data)

        

    def register_for_event(self, event_id: str, username: str) -> bool:

        if event_id in self.events:

            if username not in self.events[event_id]["registered"]:

                if len(self.events[event_id]["registered"]) < self.events[event_id].get("capacity", float('inf')):

                    self.events[event_id]["registered"].append(username)

                    return True

        return False



    def unregister_from_event(self, event_id: str, username: str) -> bool:

        if event_id in self.events and username in self.events[event_id]["registered"]:

            self.events[event_id]["registered"].remove(username)

            return True

        return False



db = Database()



def get_user_role(username: str) -> str:

    return db.users.get(username, {}).get("role", Role.GUEST.value)



def is_admin(username: str) -> bool:

    return get_user_role(username) == Role.ADMIN.value



def is_moderator(username: str) -> bool:

    return get_user_role(username) in [Role.ADMIN.value, Role.MODERATOR.value]



def format_event(event_id: str, event_data: Dict) -> str:

    registered_count = len(event_data.get("registered", []))

    capacity = event_data.get("capacity", "غير محدود")

    status_emoji = {

        EventStatus.UPCOMING.value: "🟢",

        EventStatus.ONGOING.value: "🟡",

        EventStatus.COMPLETED.value: "🔵",

        EventStatus.CANCELED.value: "🔴"

    }.get(event_data.get("status"), "⚪")

    

    return (

        f"{status_emoji} <b>{event_data['title']}</b>\n\n"

        f"📝 <b>الوصف:</b> {event_data['description']}\n"

        f"📅 <b>التاريخ:</b> {event_data['date']}\n"

        f"⏰ <b>الوقت:</b> {event_data['time']} ({event_data.get('duration', 'غير محدد')})\n"

        f"📍 <b>المكان:</b> {event_data['location']}\n"

        f"🎤 <b>المحاضر:</b> {event_data.get('speaker', 'سيتم الإعلان لاحقاً')}\n"

        f"👥 <b>المسجلون:</b> {registered_count}/{capacity}\n"

        f"🆔 <b>رقم الحدث:</b> {event_id}\n"

        f"📌 <b>الحالة:</b> {event_data.get('status')}"

    )



def format_announcement(announcement: Dict) -> str:

    priority_emoji = {

        "high": "🔴",

        "medium": "🟡",

        "low": "🟢"

    }.get(announcement.get("priority"), "⚪")

    

    return (

        f"{priority_emoji} <b>{announcement['title']}</b>\n"

        f"📅 {announcement['date']}\n\n"

        f"{announcement['content']}\n\n"

        f"{'📌 هذا الإعلان مثبت' if announcement.get('pinned') else ''}"

    )



def create_main_menu_keyboard(username: str) -> ReplyKeyboardMarkup:

    keyboard = [

        [KeyboardButton("📅 الأحداث"), KeyboardButton("📢 الإعلانات")],

        [KeyboardButton("ℹ️ معلومات النادي"), KeyboardButton("📞 اتصل بنا")]

    ]

    

    if is_moderator(username):

        keyboard.append([KeyboardButton("🛠 لوحة التحكم")])

    

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)



def create_admin_keyboard() -> List[List[InlineKeyboardButton]]:

    return [

        [InlineKeyboardButton("📅 إدارة الأحداث", callback_data="manage_events")],

        [InlineKeyboardButton("📢 إدارة الإعلانات", callback_data="manage_announcements")],

        [InlineKeyboardButton("👥 إدارة الأعضاء", callback_data="manage_users")],

        [InlineKeyboardButton("📊 الإحصائيات", callback_data="view_stats")],

        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")]

    ]



def create_event_management_keyboard() -> List[List[InlineKeyboardButton]]:

    return [

        [InlineKeyboardButton("➕ إضافة حدث", callback_data="add_event")],

        [InlineKeyboardButton("✏️ تعديل حدث", callback_data="edit_event")],

        [InlineKeyboardButton("🗑 حذف حدث", callback_data="remove_event")],

        [InlineKeyboardButton("📋 عرض الأحداث", callback_data="list_events")],

        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")]

    ]



def validate_date(date_str: str) -> bool:

    try:

        datetime.strptime(date_str, "%Y-%m-%d")

        return True

    except ValueError:

        return False



def validate_time(time_str: str) -> bool:

    try:

        datetime.strptime(time_str, "%H:%M")

        return True

    except ValueError:

        return False



def start(update: Update, context: CallbackContext) -> int:

    user = update.effective_user

    context.user_data.clear()

    

    welcome_message = (

        f"مرحباً بك {user.first_name} في بوت النادي العلمي Urex! 👋\n\n"

        "نحن مجتمع علمي يهدف إلى نشر المعرفة وتطوير المهارات التقنية.\n\n"

        "الرجاء إدخال اسم المستخدم للدخول:"

    )

    

    update.message.reply_text(welcome_message)

    return State.LOGIN_ID.value



def login_id(update: Update, context: CallbackContext) -> int:

    user_id = update.message.text.strip()

    if user_id not in db.users:

        update.message.reply_text(

            "⚠️ اسم المستخدم غير مسجل!\n"

            "الرجاء إدخال اسم مستخدم صحيح أو التواصل مع المسؤول."

        )

        return State.LOGIN_ID.value

    

    context.user_data['login_id'] = user_id

    update.message.reply_text(

        f"مرحباً {user_id}!\n"

        "الرجاء إدخال كلمة المرور:"

    )

    return State.LOGIN_PASSWORD.value



def login_password(update: Update, context: CallbackContext) -> int:

    password = update.message.text.strip()

    login_id = context.user_data.get('login_id', '')

    

    if login_id in db.users and db.users[login_id]["password"] == password:

        # Success login

        context.user_data['authenticated'] = True

        user_data = db.users[login_id]

        

        welcome_back = (

            f"✅ تم تسجيل الدخول بنجاح، {user_data.get('full_name', login_id)}!\n\n"

            f"🔹 الدور: {user_data['role'].capitalize()}\n"

            f"🔹 تاريخ الانضمام: {user_data.get('join_date', 'غير معروف')}\n\n"

            "يمكنك الآن استخدام القائمة أدناه للتفاعل مع البوت:"

        )

        

        update.message.reply_text(

            welcome_back,

            reply_markup=create_main_menu_keyboard(login_id)

        )

        

        pinned_announcements = [a for a in db.announcements if a.get("pinned")]

        if pinned_announcements:

            update.message.reply_text("📌 الإعلانات المثبتة:")

            for announcement in pinned_announcements:

                update.message.reply_text(

                    format_announcement(announcement),

                    parse_mode='HTML'

                )

        

        return State.AUTHENTICATED.value

    else:

        update.message.reply_text(

            "❌ كلمة المرور غير صحيحة!\n"

            "الرجاء إدخال اسم المستخدم مرة أخرى:"

        )

        return State.LOGIN_ID.value



def help_command(update: Update, context: CallbackContext) -> None:

    username = context.user_data.get('login_id', '')

    help_text = (

        "🛠 <b>أوامر البوت:</b>\n\n"

        "📌 <b>القائمة الرئيسية:</b>\n"

        "- 📅 الأحداث: عرض الأحداث القادمة\n"

        "- 📢 الإعلانات: عرض الإعلانات المهمة\n"

        "- ℹ️ معلومات النادي: عن النادي ورسالته\n"

        "- 📞 اتصل بنا: معلومات التواصل مع النادي\n"

        "- ✍️ تقديم اقتراح: إرسال ملاحظاتك أو اقتراحاتك\n\n"

    )

    

    if is_moderator(username):

        help_text += (

            "🛠 <b>أوامر المسؤولين:</b>\n"

            "- 🛠 لوحة التحكم: الوصول إلى لوحة إدارة النادي\n"

            "- /broadcast: إرسال إشعار لجميع الأعضاء (للمشرفين فقط)\n"

        )

    

    update.message.reply_text(help_text, parse_mode='HTML')



def club_info(update: Update, context: CallbackContext) -> None:

    info_text = (

        "🔬 <b>النادي العلمي Urex</b>\n\n"

        "نادي Urex نادي علمي نشأ بولاية تيسمسيلت على يد السيد: عبد الغاني جودي والسيد: عمار بومدين ويهدف إلى ترقية المكتسبات وإضافة خبرات جديد للأعضاء وهو أول نادي في تيسمسيلت يستضاف من قبل الولايات الأخرى و أول نادي يضم أكبر المبرمجين في ولاية تيسمسيلت و أول نادي في الشمال الجزائري يهدف إلى السيادة العربية.\n\n"

        "📌 <b>رؤيتنا:</b>\n"

        "الوصول إلى السيادة الوطنية للنوادي العلمية والسيطرة على كل النوادي وتطوير أكبر تضامن للنوادي في إفريقيا\n\n"

        "🎯 <b>أهدافنا:</b>\n"

        "- تنظيم فعاليات وورش عمل علمية\n"

        "- تشجيع الابتكار والإبداع العلمي\n"

        "- بناء جسر بين الطلاب والمتخصصين\n"

        "- تنمية مهارات الطلاب التقنية\n\n"

        "🏆 <b>إنجازاتنا:</b>\n"

        "- تنظيم ورشة الأردوينو\n"

        "- المشاركة في المسابقة الوطنية للبيئة وإعادة التدوير والحصول على المركز الأول\n"

        "- إنشاء طالب 5 نجوم\n\n"

        "انضم إلينا وساهم في بناء مجتمع علمي متميز!"

    )



    update.message.reply_text(info_text, parse_mode='HTML')



def contact_info(update: Update, context: CallbackContext) -> None:

    contact_text = (

        "📞 <b>معلومات التواصل:</b>\n\n"

        "📍 <b>المقر:</b> جامعة تيسمسيلت - كلية العلوم والتكنولوجيا\n"

        "📧 <b>البريد الإلكتروني:</b> urex.club@univ-tissemsilt.dz\n"

        "📱 <b>الهاتف:</b> +213 *********\n\n"

        "👥 <b>فريق الإدارة:</b>\n"

        "- جودي عبد الغاني (رئيس النادي)\n"

        "- بومدين عومار (نائب رئيس النادي)\n"

        "- أمين داشير (مسؤول الفعاليات)\n"

        "- مهلول أشرف (مبرمج ومطور النادي)"

    )

    

    update.message.reply_text(contact_text, parse_mode='HTML')



def list_events(update: Update, context: CallbackContext) -> None:

    if not db.events:

        update.message.reply_text("⚠️ لا توجد أحداث متاحة حالياً.")

        return

    

    events_by_status = {

        EventStatus.UPCOMING.value: [],

        EventStatus.ONGOING.value: [],

        EventStatus.COMPLETED.value: [],

        EventStatus.CANCELED.value: []

    }

    

    for event_id, event_data in db.events.items():

        status = event_data.get("status")

        if status in events_by_status:

            events_by_status[status].append((event_id, event_data))

    

    for status, events in events_by_status.items():

        if events:

            status_name = {

                EventStatus.UPCOMING.value: "🟢 الأحداث القادمة",

                EventStatus.ONGOING.value: "🟡 الأحداث الجارية",

                EventStatus.COMPLETED.value: "🔵 الأحداث المنتهية",

                EventStatus.CANCELED.value: "🔴 الأحداث الملغاة"

            }.get(status, "الأحداث")

            

            update.message.reply_text(f"<b>{status_name}</b>", parse_mode='HTML')

            

            for event_id, event_data in events:

                keyboard = [

                    [InlineKeyboardButton(

                        "عرض التفاصيل", 

                        callback_data=f"event_detail_{event_id}"

                    )]

                ]

                

                if status == EventStatus.UPCOMING.value:

                    keyboard[0].append(InlineKeyboardButton(

                        "التسجيل", 

                        callback_data=f"register_{event_id}"

                    ))

                

                reply_markup = InlineKeyboardMarkup(keyboard)

                

                update.message.reply_text(

                    f"📌 <b>{event_data['title']}</b>\n"

                    f"📅 {event_data['date']} | ⏰ {event_data['time']}\n"

                    f"📍 {event_data['location']}",

                    reply_markup=reply_markup,

                    parse_mode='HTML'

                )



def event_detail(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[2]

    event_data = db.events.get(event_id)

    username = context.user_data.get('login_id', '')

    

    if not event_data:

        query.edit_message_text("⚠️ حدث غير موجود أو تم إلغاؤه.")

        return

    

    keyboard = []

    

    if event_data.get("status") == EventStatus.UPCOMING.value:

        if username in event_data.get("registered", []):

            keyboard.append([InlineKeyboardButton(

                "إلغاء التسجيل", 

                callback_data=f"unregister_{event_id}"

            )])

        else:

            if len(event_data.get("registered", [])) < event_data.get("capacity", float('inf')):

                keyboard.append([InlineKeyboardButton(

                    "التسجيل في الحدث", 

                    callback_data=f"register_{event_id}"

                )])

            else:

                keyboard.append([InlineKeyboardButton(

                    "الحدث ممتلئ", 

                    callback_data=f"event_full_{event_id}"

                )])

    

    if is_moderator(username):

        keyboard.append([

            InlineKeyboardButton("تعديل", callback_data=f"edit_event_{event_id}"),

            InlineKeyboardButton("حذف", callback_data=f"delete_event_{event_id}")

        ])

    

    keyboard.append([InlineKeyboardButton("رجوع", callback_data="back_to_events")])

    

    reply_markup = InlineKeyboardMarkup(keyboard)

    

    query.edit_message_text(

        text=format_event(event_id, event_data),

        reply_markup=reply_markup,

        parse_mode='HTML'

    )



def register_for_event(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[1]

    username = context.user_data.get('login_id', '')

    

    if not username:

        query.edit_message_text("⚠️ يجب تسجيل الدخول أولاً!")

        return

    

    if db.register_for_event(event_id, username):

        query.edit_message_text(

            f"✅ تم تسجيلك في الحدث بنجاح!\n\n"

            f"سيتم إعلامك بأي تحديثات حول الحدث."

        )

    else:

        query.edit_message_text("❌ حدث خطأ أثناء محاولة التسجيل!")



def unregister_from_event(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[1]

    username = context.user_data.get('login_id', '')

    

    if db.unregister_from_event(event_id, username):

        query.edit_message_text("✅ تم إلغاء تسجيلك من الحدث بنجاح!")

    else:

        query.edit_message_text("❌ حدث خطأ أثناء محاولة إلغاء التسجيل!")



def list_announcements(update: Update, context: CallbackContext) -> None:

    if not db.announcements:

        update.message.reply_text("⚠️ لا توجد إعلانات حالياً.")

        return

    

    sorted_announcements = sorted(

        db.announcements,

        key=lambda x: (x.get("priority") != "high", x.get("date")),

        reverse=True

    )

    

    update.message.reply_text("📢 <b>الإعلانات:</b>", parse_mode='HTML')

    

    for announcement in sorted_announcements:

        keyboard = []

        if is_moderator(context.user_data.get('login_id', '')):

            keyboard.append([

                InlineKeyboardButton("حذف", callback_data=f"delete_announce_{announcement['id']}")

            ])

        

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        

        update.message.reply_text(

            format_announcement(announcement),

            reply_markup=reply_markup,

            parse_mode='HTML'

        )



def admin_panel(update: Update, context: CallbackContext) -> int:

    username = context.user_data.get('login_id', '')

    if not is_moderator(username):

        update.message.reply_text("⛔ ليس لديك صلاحية الدخول لهذه الصفحة!")

        return State.AUTHENTICATED.value

    

    update.message.reply_text(

        "🛠 <b>لوحة تحكم المسؤول:</b>\n\n"

        "اختر أحد الخيارات التالية:",

        reply_markup=InlineKeyboardMarkup(create_admin_keyboard()),

        parse_mode='HTML'

    )

    return State.ADMIN_PANEL.value



def manage_events(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    query.edit_message_text(

        "📅 <b>إدارة الأحداث:</b>\n\n"

        "اختر الإجراء المطلوب:",

        reply_markup=InlineKeyboardMarkup(create_event_management_keyboard()),

        parse_mode='HTML'

    )

    return State.EVENT_MANAGEMENT.value



def start_add_event(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    context.user_data['event_data'] = {}

    

    query.edit_message_text(

        "➕ <b>إضافة حدث جديد:</b>\n\n"

        "الرجاء إرسال عنوان الحدث:",

        parse_mode='HTML'

    )

    return State.ADD_EVENT.value



def process_add_event(update: Update, context: CallbackContext) -> int:

    event_data = context.user_data.get('event_data', {})

    username = context.user_data.get('login_id', '')

    

    if 'title' not in event_data:

        event_data['title'] = update.message.text

        update.message.reply_text(

            "📝 الرجاء إرسال وصف مفصل للحدث:"

        )

        return State.ADD_EVENT.value

    

    elif 'description' not in event_data:

        event_data['description'] = update.message.text

        update.message.reply_text(

            "📅 الرجاء إرسال تاريخ الحدث (YYYY-MM-DD):"

        )

        return State.ADD_EVENT.value

    

    elif 'date' not in event_data:

        if not validate_date(update.message.text):

            update.message.reply_text(

                "⚠️ صيغة التاريخ غير صحيحة! الرجاء استخدام الصيغة YYYY-MM-DD:"

            )

            return State.ADD_EVENT.value

        

        event_data['date'] = update.message.text

        update.message.reply_text(

            "⏰ الرجاء إرسال وقت الحدث (HH:MM):"

        )

        return State.ADD_EVENT.value

    

    elif 'time' not in event_data:

        if not validate_time(update.message.text):

            update.message.reply_text(

                "⚠️ صيغة الوقت غير صحيحة! الرجاء استخدام الصيغة HH:MM:"

            )

            return State.ADD_EVENT.value

        

        event_data['time'] = update.message.text

        update.message.reply_text(

            "⏳ الرجاء إرسال مدة الحدث (مثال: ساعتان):"

        )

        return State.ADD_EVENT.value

    

    elif 'duration' not in event_data:

        event_data['duration'] = update.message.text

        update.message.reply_text(

            "📍 الرجاء إرسال مكان انعقاد الحدث:"

        )

        return State.ADD_EVENT.value

    

    elif 'location' not in event_data:

        event_data['location'] = update.message.text

        update.message.reply_text(

            "🎤 الرجاء إرسال اسم المحاضر (أو اكتب 'تخطى' إذا لم يتحدد بعد):"

        )

        return State.ADD_EVENT.value

    

    elif 'speaker' not in event_data:

        speaker = update.message.text

        if speaker.lower() != 'تخطى':

            event_data['speaker'] = speaker

        else:

            event_data['speaker'] = "سيتم الإعلان لاحقاً"

        

        update.message.reply_text(

            "👥 الرجاء إرسال السعة القصوى للحضور (أو اكتب 'غير محدود'):"

        )

        return State.ADD_EVENT.value

    

    elif 'capacity' not in event_data:

        capacity = update.message.text

        if capacity.lower() == 'غير محدود':

            event_data['capacity'] = float('inf')

        else:

            try:

                event_data['capacity'] = int(capacity)

            except ValueError:

                update.message.reply_text(

                    "⚠️ يجب إدخال رقم صحيح! الرجاء إعادة المحاولة:"

                )

                return State.ADD_EVENT.value

        

        event_data['registered'] = [username]

        

        event_id = db.add_event(event_data)

        

        update.message.reply_text(

            f"✅ تم إضافة الحدث بنجاح!\n\n"

            f"{format_event(event_id, event_data)}",

            parse_mode='HTML'

        )

        

        context.user_data.pop('event_data', None)

        

        return admin_panel(update, context)



def start_edit_event(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    if not db.events:

        query.edit_message_text("⚠️ لا توجد أحداث متاحة للتعديل!")

        return State.EVENT_MANAGEMENT.value

    

    keyboard = [

        [InlineKeyboardButton(

            f"{event_data['title']} (ID: {event_id})", 

            callback_data=f"edit_event_{event_id}"

        )]

        for event_id, event_data in db.events.items()

    ]

    keyboard.append([InlineKeyboardButton("إلغاء", callback_data="back_to_events")])

    

    query.edit_message_text(

        "✏️ <b>تعديل حدث:</b>\n\n"

        "اختر الحدث الذي تريد تعديله:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.EDIT_EVENT.value



def edit_event_options(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[2]

    event_data = db.events.get(event_id)

    

    if not event_data:

        query.edit_message_text("⚠️ حدث غير موجود!")

        return State.EVENT_MANAGEMENT.value

    

    context.user_data['editing_event'] = event_id

    

    keyboard = [

        [InlineKeyboardButton("العنوان", callback_data=f"edit_field_title_{event_id}")],

        [InlineKeyboardButton("الوصف", callback_data=f"edit_field_description_{event_id}")],

        [InlineKeyboardButton("التاريخ", callback_data=f"edit_field_date_{event_id}")],

        [InlineKeyboardButton("الوقت", callback_data=f"edit_field_time_{event_id}")],

        [InlineKeyboardButton("المكان", callback_data=f"edit_field_location_{event_id}")],

        [InlineKeyboardButton("المحاضر", callback_data=f"edit_field_speaker_{event_id}")],

        [InlineKeyboardButton("الحالة", callback_data=f"edit_field_status_{event_id}")],

        [InlineKeyboardButton("إلغاء", callback_data="back_to_events")]

    ]

    

    query.edit_message_text(

        f"✏️ <b>تعديل الحدث:</b>\n\n"

        f"{format_event(event_id, event_data)}\n\n"

        "اختر الحقل الذي تريد تعديله:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.EDIT_EVENT.value



def process_edit_field(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    parts = query.data.split('_')

    field = parts[2]

    event_id = parts[3]

    

    context.user_data['editing_field'] = field

    context.user_data['editing_event'] = event_id

    

    field_names = {

        'title': 'العنوان',

        'description': 'الوصف',

        'date': 'التاريخ (YYYY-MM-DD)',

        'time': 'الوقت (HH:MM)',

        'location': 'المكان',

        'speaker': 'المحاضر',

        'status': 'الحالة'

    }

    

    query.edit_message_text(

        f"✏️ الرجاء إرسال {field_names[field]} الجديد:"

    )

    return State.EDIT_EVENT.value



def save_edited_field(update: Update, context: CallbackContext) -> int:

    event_id = context.user_data.get('editing_event')

    field = context.user_data.get('editing_field')

    new_value = update.message.text

    

    if not event_id or not field:

        update.message.reply_text("⚠️ حدث خطأ في عملية التعديل!")

        return State.EVENT_MANAGEMENT.value

    

    if field == 'date' and not validate_date(new_value):

        update.message.reply_text(

            "⚠️ صيغة التاريخ غير صحيحة! الرجاء استخدام الصيغة YYYY-MM-DD:"

        )

        return State.EDIT_EVENT.value

    

    if field == 'time' and not validate_time(new_value):

        update.message.reply_text(

            "⚠️ صيغة الوقت غير صحيحة! الرجاء استخدام الصيغة HH:MM:"

        )

        return State.EDIT_EVENT.value

    

    updates = {field: new_value}

    

    if field == 'status':

        if new_value not in [s.value for s in EventStatus]:

            update.message.reply_text(

                "⚠️ حالة غير صالحة! الرجاء اختيار من:\n"

                f"{', '.join([s.value for s in EventStatus])}"

            )

            return State.EDIT_EVENT.value

    

    if db.update_event(event_id, updates):

        update.message.reply_text(

            f"✅ تم تحديث {field} بنجاح!"

        )

    else:

        update.message.reply_text("❌ حدث خطأ أثناء التحديث!")

    

    context.user_data.pop('editing_event', None)

    context.user_data.pop('editing_field', None)

    

    return admin_panel(update, context)



def start_remove_event(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    if not db.events:

        query.edit_message_text("⚠️ لا توجد أحداث متاحة للحذف!")

        return State.EVENT_MANAGEMENT.value

    

    keyboard = [

        [InlineKeyboardButton(

            f"{event_data['title']} (ID: {event_id})", 

            callback_data=f"confirm_delete_{event_id}"

        )]

        for event_id, event_data in db.events.items()

    ]

    keyboard.append([InlineKeyboardButton("إلغاء", callback_data="back_to_events")])

    

    query.edit_message_text(

        "🗑 <b>حذف حدث:</b>\n\n"

        "اختر الحدث الذي تريد حذفه:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.REMOVE_EVENT.value



def confirm_delete_event(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[2]

    event_data = db.events.get(event_id)

    

    if not event_data:

        query.edit_message_text("⚠️ حدث غير موجود!")

        return State.EVENT_MANAGEMENT.value

    

    keyboard = [

        [InlineKeyboardButton("✅ نعم، احذف", callback_data=f"delete_event_{event_id}")],

        [InlineKeyboardButton("❌ إلغاء", callback_data="back_to_events")]

    ]

    

    query.edit_message_text(

        f"⚠️ <b>تأكيد الحذف:</b>\n\n"

        f"هل أنت متأكد من حذف هذا الحدث؟\n\n"

        f"{event_data['title']}\n"

        f"ID: {event_id}\n\n"

        "⚠️ لا يمكن التراجع عن هذه العملية!",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.REMOVE_EVENT.value



def remove_event(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    event_id = query.data.split('_')[2]

    event_data = db.events.get(event_id)

    

    if event_data and db.remove_event(event_id):

        query.edit_message_text(

            f"✅ تم حذف الحدث بنجاح:\n\n"

            f"{event_data['title']} - {event_data['date']}"

        )

    else:

        query.edit_message_text("❌ حدث خطأ أثناء محاولة حذف الحدث!")

    

    return admin_panel(update, context)



def manage_announcements(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    keyboard = [

        [InlineKeyboardButton("➕ إضافة إعلان", callback_data="add_announcement")],

        [InlineKeyboardButton("🗑 حذف إعلان", callback_data="remove_announcement")],

        [InlineKeyboardButton("📋 عرض الإعلانات", callback_data="list_announcements_admin")],

        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")]

    ]

    

    query.edit_message_text(

        "📢 <b>إدارة الإعلانات:</b>\n\n"

        "اختر الإجراء المطلوب:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.ANNOUNCEMENT_MANAGEMENT.value



def start_add_announcement(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    context.user_data['announcement_data'] = {}

    

    query.edit_message_text(

        "➕ <b>إضافة إعلان جديد:</b>\n\n"

        "الرجاء إرسال عنوان الإعلان:",

        parse_mode='HTML'

    )

    return State.ADD_ANNOUNCEMENT.value



def process_add_announcement(update: Update, context: CallbackContext) -> int:

    announcement_data = context.user_data.get('announcement_data', {})

    

    if 'title' not in announcement_data:

        announcement_data['title'] = update.message.text

        update.message.reply_text(

            "📝 الرجاء إرسال محتوى الإعلان:"

        )

        return State.ADD_ANNOUNCEMENT.value

    

    elif 'content' not in announcement_data:

        announcement_data['content'] = update.message.text

        update.message.reply_text(

            "🔺 حدد أولوية الإعلان (عالي/متوسط/منخفض):"

        )

        return State.ADD_ANNOUNCEMENT.value

    

    elif 'priority' not in announcement_data:

        priority = update.message.text.lower()

        if priority not in ['عالي', 'متوسط', 'منخفض']:

            update.message.reply_text(

                "⚠️ أولوية غير صالحة! الرجاء اختيار من: عالي، متوسط، منخفض"

            )

            return State.ADD_ANNOUNCEMENT.value

        

        announcement_data['priority'] = priority

        update.message.reply_text(

            "📌 هل تريد تثبيت هذا الإعلان؟ (نعم/لا):"

        )

        return State.ADD_ANNOUNCEMENT.value

    

    elif 'pinned' not in announcement_data:

        pinned = update.message.text.lower()

        if pinned not in ['نعم', 'لا']:

            update.message.reply_text(

                "⚠️ إجابة غير صالحة! الرجاء الإجابة بنعم أو لا"

            )

            return State.ADD_ANNOUNCEMENT.value

        

        announcement_data['pinned'] = (pinned == 'نعم')

        

        announcement_id = db.add_announcement(announcement_data)

        

        update.message.reply_text(

            f"✅ تم نشر الإعلان بنجاح (ID: {announcement_id})!\n\n"

            f"{format_announcement(announcement_data)}",

            parse_mode='HTML'

        )

        

        context.user_data.pop('announcement_data', None)

        

        return admin_panel(update, context)



def list_announcements_admin(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    if not db.announcements:

        query.edit_message_text("⚠️ لا توجد إعلانات حالياً.")

        return

    

    sorted_announcements = sorted(

        db.announcements,

        key=lambda x: (x.get("priority") != "high", x.get("date")),

        reverse=True

    )

    

    query.edit_message_text("📢 <b>الإعلانات:</b>", parse_mode='HTML')

    

    for announcement in sorted_announcements:

        keyboard = [

            [InlineKeyboardButton("حذف", callback_data=f"delete_announce_{announcement['id']}")]

        ]

        

        reply_markup = InlineKeyboardMarkup(keyboard)

        

        context.bot.send_message(

            chat_id=query.message.chat_id,

            text=format_announcement(announcement),

            reply_markup=reply_markup,

            parse_mode='HTML'

        )

    

    return State.ANNOUNCEMENT_MANAGEMENT.value



def remove_announcement(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    if not db.announcements:

        query.edit_message_text("⚠️ لا توجد إعلانات حالياً.")

        return State.ANNOUNCEMENT_MANAGEMENT.value

    

    keyboard = [

        [InlineKeyboardButton(

            f"{a['title']} (ID: {a['id']})", 

            callback_data=f"confirm_delete_announce_{a['id']}"

        )]

        for a in db.announcements

    ]

    keyboard.append([InlineKeyboardButton("إلغاء", callback_data="back_to_announcements")])

    

    query.edit_message_text(

        "🗑 <b>حذف إعلان:</b>\n\n"

        "اختر الإعلان الذي تريد حذفه:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.ANNOUNCEMENT_MANAGEMENT.value



def confirm_delete_announcement(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    announce_id = int(query.data.split('_')[3])

    announcement = next((a for a in db.announcements if a['id'] == announce_id), None)

    

    if not announcement:

        query.edit_message_text("⚠️ إعلان غير موجود!")

        return State.ANNOUNCEMENT_MANAGEMENT.value

    

    keyboard = [

        [InlineKeyboardButton("✅ نعم، احذف", callback_data=f"delete_announce_{announce_id}")],

        [InlineKeyboardButton("❌ إلغاء", callback_data="back_to_announcements")]

    ]

    

    query.edit_message_text(

        f"⚠️ <b>تأكيد الحذف:</b>\n\n"

        f"هل أنت متأكد من حذف هذا الإعلان؟\n\n"

        f"{announcement['title']}\n"

        f"ID: {announce_id}\n\n"

        "⚠️ لا يمكن التراجع عن هذه العملية!",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.ANNOUNCEMENT_MANAGEMENT.value



def delete_announcement(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    announce_id = int(query.data.split('_')[2])

    

    for i, a in enumerate(db.announcements):

        if a['id'] == announce_id:

            deleted_title = a['title']

            del db.announcements[i]

            db.statistics["announcements_count"] -= 1

            break

    else:

        query.edit_message_text("❌ إعلان غير موجود!")

        return State.ANNOUNCEMENT_MANAGEMENT.value

    

    query.edit_message_text(

        f"✅ تم حذف الإعلان بنجاح:\n\n"

        f"{deleted_title}"

    )

    

    return admin_panel(update, context)



def manage_users(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    if not is_admin(context.user_data.get('login_id', '')):

        query.edit_message_text("⛔ ليس لديك صلاحية الدخول لهذه الصفحة!")

        return State.ADMIN_PANEL.value

    

    keyboard = [

        [InlineKeyboardButton("عرض الأعضاء", callback_data="list_users")],

        [InlineKeyboardButton("تغيير صلاحيات", callback_data="change_roles")],

        [InlineKeyboardButton("إحصائيات الأعضاء", callback_data="user_stats")],

        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")]

    ]

    

    query.edit_message_text(

        "👥 <b>إدارة الأعضاء:</b>\n\n"

        "اختر الإجراء المطلوب:",

        reply_markup=InlineKeyboardMarkup(keyboard),

        parse_mode='HTML'

    )

    return State.USER_MANAGEMENT.value



def list_users(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    if not db.users:

        query.edit_message_text("⚠️ لا يوجد أعضاء مسجلين!")

        return

    

    users_by_role = {

        Role.ADMIN.value: [],

        Role.MODERATOR.value: [],

        Role.MEMBER.value: []

    }

    

    for username, user_data in db.users.items():

        role = user_data.get("role")

        if role in users_by_role:

            users_by_role[role].append((username, user_data))

    

    response = "👥 <b>قائمة الأعضاء:</b>\n\n"

    

    for role, users in users_by_role.items():

        if users:

            role_name = {

                Role.ADMIN.value: "👑 المشرفون",

                Role.MODERATOR.value: "🛠 المشرفون المساعدون",

                Role.MEMBER.value: "👤 الأعضاء"

            }.get(role, "الأعضاء")

            

            response += f"<b>{role_name}:</b>\n"

            

            for username, user_data in users:

                response += (

                    f"- {user_data.get('full_name', username)} "

                    f"(@{username}) - {user_data.get('join_date', 'غير معروف')}\n"

                )

            

            response += "\n"

    

    query.edit_message_text(

        response,

        parse_mode='HTML'

    )

    return State.USER_MANAGEMENT.value



def view_stats(update: Update, context: CallbackContext) -> None:

    query = update.callback_query

    query.answer()

    

    stats = db.statistics

    active_events = sum(1 for e in db.events.values() if e.get("status") == EventStatus.UPCOMING.value)

    

    response = (

        "📊 <b>إحصائيات النادي:</b>\n\n"

        f"👥 <b>إجمالي الأعضاء:</b> {stats['total_users']}\n"

        f"🟢 <b>الأعضاء النشطون:</b> {stats['active_users']}\n\n"

        f"📅 <b>إجمالي الأحداث:</b> {stats['total_events']}\n"

        f"🟢 <b>الأحداث القادمة:</b> {active_events}\n\n"

        f"📢 <b>عدد الإعلانات:</b> {stats['announcements_count']}\n\n"

        "🔄 <b>تاريخ التحديث:</b> " + datetime.now().strftime("%Y-%m-%d %H:%M")

    )

    

    query.edit_message_text(

        response,

        parse_mode='HTML'

    )

    return State.ADMIN_PANEL.value



def feedback_handler(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(

        "✍️ <b>نموذج الملاحظات والاقتراحات:</b>\n\n"

        "نحن نقدر ملاحظاتك واقتراحاتك لتحسين النادي وخدماته.\n"

        "الرجاء إرسال ملاحظتك أو اقتراحك وسيتم مراجعته من قبل الفريق:",

        parse_mode='HTML'

    )

    return State.FEEDBACK.value



def process_feedback(update: Update, context: CallbackContext) -> int:

    feedback_text = update.message.text

    username = context.user_data.get('login_id', 'زائر')

    

    db.add_feedback({

        "user": username,

        "text": feedback_text

    })

    

    update.message.reply_text(

        "شكراً لك على ملاحظاتك القيمة! 🤝\n"

        "سيتم مراجعة اقتراحك من قبل الفريق المسؤول."

    )

    

    admins = [u for u, d in db.users.items() if d.get("role") == Role.ADMIN.value]

    for admin in admins:

        try:

            context.bot.send_message(

                chat_id=admin,

                text=f"📢 ملاحظة جديدة من {username}:\n\n{feedback_text}"

            )

        except Exception as e:

            logger.error(f"Failed to send feedback to admin {admin}: {e}")

    

    return State.AUTHENTICATED.value



def broadcast_message(update: Update, context: CallbackContext) -> None:

    username = context.user_data.get('login_id', '')

    if not is_admin(username):

        update.message.reply_text("⛔ ليس لديك صلاحية استخدام هذا الأمر!")

        return

    

    if not context.args:

        update.message.reply_text(

            "ℹ️ الاستخدام: /broadcast <الرسالة>\n\n"

            "مثال:\n"

            "/broadcast سيتم عقد اجتماع غداً في الساعة 4 مساءً"

        )

        return

    

    message = ' '.join(context.args)

    sent = 0

    failed = 0

    

    for user in db.users:

        try:

            context.bot.send_message(

                chat_id=user,

                text=f"📢 إعلان عام من الإدارة:\n\n{message}"

            )

            sent += 1

        except Exception as e:

            logger.error(f"Failed to send broadcast to {user}: {e}")

            failed += 1

    

    update.message.reply_text(

        f"✅ تم إرسال الإعلان إلى {sent} عضو\n"

        f"❌ فشل الإرسال إلى {failed} عضو"

    )



def back_to_main(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    query.answer()

    

    username = context.user_data.get('login_id', '')

    

    query.edit_message_text(

        "تم العودة إلى القائمة الرئيسية.",

        reply_markup=create_main_menu_keyboard(username)

    )

    return State.AUTHENTICATED.value



def back_to_admin(update: Update, context: CallbackContext) -> int:

    return admin_panel(update, context)



def back_to_events(update: Update, context: CallbackContext) -> int:

    return manage_events(update, context)



def back_to_announcements(update: Update, context: CallbackContext) -> int:

    return manage_announcements(update, context)



def cancel(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(

        "تم إلغاء العملية الحالية.",

        reply_markup=create_main_menu_keyboard(context.user_data.get('login_id', ''))

    )

    return State.AUTHENTICATED.value



def error_handler(update: Update, context: CallbackContext) -> None:

    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    

    if update and update.effective_message:

        update.effective_message.reply_text(

            "⚠️ حدث خطأ غير متوقع!\n"

            "تم إبلاغ الفريق التقني بالمشكلة.\n"

            "الرجاء المحاولة مرة أخرى لاحقاً."

        )



def main() -> None:
    try:
        if os.path.exists('urex_bot_data.pickle'):
            os.remove('urex_bot_data.pickle')
    except Exception as e:
        logger.warning(f"Could not delete old data file: {e}")

    persistence = PicklePersistence(filepath='urex_bot_data.pickle')
    
    updater = Updater("التوكن هنا تحصل عليه من BOTFATHER في الTELEGRAM منقدرش نحط تاعي ديزولي", persistence=persistence, use_context=True)
    dp = updater.dispatcher

    

    conv_handler = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={

            State.LOGIN_ID.value: [

                MessageHandler(filters.text & ~filters.command, login_id)

            ],

            State.LOGIN_PASSWORD.value: [

                MessageHandler(filters.text & ~filters.command, login_password)

            ],

            State.AUTHENTICATED.value: [

                MessageHandler(filters.regex('^📅 الأحداث$'), list_events),

                MessageHandler(filters.regex('^📢 الإعلانات$'), list_announcements),

                MessageHandler(filters.regex('^ℹ️ معلومات النادي$'), club_info),

                MessageHandler(filters.regex('^📞 اتصل بنا$'), contact_info),

                MessageHandler(filters.regex('^✍️ تقديم اقتراح$'), feedback_handler),

                MessageHandler(filters.regex('^🛠 لوحة التحكم$'), admin_panel),

                CommandHandler('help', help_command),

                CommandHandler('events', list_events),

                CommandHandler('announcements', list_announcements),

                CommandHandler('contact', contact_info),

                CommandHandler('feedback', feedback_handler),

                CommandHandler('admin', admin_panel),

                MessageHandler(filters.text & ~filters.command, help_command)

            ],

            State.ADMIN_PANEL.value: [

                CallbackQueryHandler(manage_events, pattern='^manage_events$'),

                CallbackQueryHandler(manage_announcements, pattern='^manage_announcements$'),

                CallbackQueryHandler(manage_users, pattern='^manage_users$'),

                CallbackQueryHandler(view_stats, pattern='^view_stats$'),

                CallbackQueryHandler(back_to_main, pattern='^back_to_main$')

            ],

            State.EVENT_MANAGEMENT.value: [

                CallbackQueryHandler(start_add_event, pattern='^add_event$'),

                CallbackQueryHandler(start_edit_event, pattern='^edit_event$'),

                CallbackQueryHandler(start_remove_event, pattern='^remove_event$'),

                CallbackQueryHandler(list_events, pattern='^list_events$'),

                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')

            ],

            State.ADD_EVENT.value: [

                MessageHandler(filters.text & ~filters.command, process_add_event),

                CommandHandler('cancel', cancel)

            ],

            State.EDIT_EVENT.value: [

                CallbackQueryHandler(edit_event_options, pattern='^edit_event_'),

                CallbackQueryHandler(process_edit_field, pattern='^edit_field_'),

                MessageHandler(filters.text & ~filters.command, save_edited_field),

                CallbackQueryHandler(back_to_events, pattern='^back_to_events$'),

                CommandHandler('cancel', cancel)

            ],

            State.REMOVE_EVENT.value: [

                CallbackQueryHandler(confirm_delete_event, pattern='^confirm_delete_'),

                CallbackQueryHandler(remove_event, pattern='^delete_event_'),

                CallbackQueryHandler(back_to_events, pattern='^back_to_events$')

            ],

            State.ANNOUNCEMENT_MANAGEMENT.value: [

                CallbackQueryHandler(start_add_announcement, pattern='^add_announcement$'),

                CallbackQueryHandler(remove_announcement, pattern='^remove_announcement$'),

                CallbackQueryHandler(list_announcements_admin, pattern='^list_announcements_admin$'),

                CallbackQueryHandler(confirm_delete_announcement, pattern='^confirm_delete_announce_'),

                CallbackQueryHandler(delete_announcement, pattern='^delete_announce_'),

                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')

            ],

            State.ADD_ANNOUNCEMENT.value: [

                MessageHandler(filters.text & ~filters.command, process_add_announcement),

                CommandHandler('cancel', cancel)

            ],

            State.USER_MANAGEMENT.value: [

                CallbackQueryHandler(list_users, pattern='^list_users$'),

                CallbackQueryHandler(back_to_admin, pattern='^back_to_admin$')

            ],

            State.FEEDBACK.value: [

                MessageHandler(filters.text & ~filters.command, process_feedback),

                CommandHandler('cancel', cancel)

            ]

        },

        fallbacks=[CommandHandler('cancel', cancel)],

        name="urex_bot_conversation",

        persistent=True

    )

    

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('broadcast', broadcast_message))

    

    dp.add_handler(CallbackQueryHandler(event_detail, pattern='^event_detail_'))

    dp.add_handler(CallbackQueryHandler(register_for_event, pattern='^register_'))

    dp.add_handler(CallbackQueryHandler(unregister_from_event, pattern='^unregister_'))

    

    dp.add_error_handler(error_handler)

    

    updater.start_polling()

    logger.info("Bot started and polling...")

    updater.idle()



if __name__ == '__main__':


    main()
