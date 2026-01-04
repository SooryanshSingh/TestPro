import json
import uuid
from collections import defaultdict
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ExamAuditLog


EXAM_SESSIONS = defaultdict(dict)


class ExamControlConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def log_action(self, action, target=None):
        ExamAuditLog.objects.create(
            exam_id=self.exam_id,
            actor=self.scope["user"] if self.scope["user"].is_authenticated else None,
            action=action,
            target=target
        )
    
    async def connect(self):
        self.exam_id = self.scope['url_route']['kwargs']['exam_id']
        self.room_group_name = f'exam_{self.exam_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "close_exam":
            

            await self.log_action(
                action="EXAM_CLOSED",
                target=f"exam_{self.exam_id}"
            )
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "exam_closed_message"}
            )
        if data.get("type") == "warn_student":
            await self.log_action(
                action="WARNING_SENT",
                target=f"exam_{self.exam_id}"
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "warning_message"}
            )
            
        


    async def exam_closed_message(self, event):
        await self.send(text_data=json.dumps({"type": "exam_closed"}))
    async def warning_message(self, event):
        await self.send(text_data=json.dumps({
        "type": "warning_message"
    }))




EXAM_SESSIONS = defaultdict(dict)


EXAM_SESSIONS = defaultdict(dict)


class TabMonitorConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def log_tab_change(self):
        ExamAuditLog.objects.create(
            exam_id=self.exam_id,
            actor=self.user if self.user.is_authenticated else None,
            action="TAB_CHANGE",
            target=self.session_id
        )
    @database_sync_to_async
    def check_is_proctor(self):
        return (
            self.user.is_authenticated
            and self.user.groups.filter(name="Proctor").exists()
        )

    async def connect(self):
        self.exam_id = self.scope['url_route']['kwargs']['exam_id']
        self.user = self.scope["user"]

        self.proctor_group = f"exam_{self.exam_id}_proctors"
        self.student_group = f"exam_{self.exam_id}_students"

        self.is_proctor = await self.check_is_proctor()

        if self.is_proctor:
            await self.channel_layer.group_add(
                self.proctor_group,
                self.channel_name
            )
        else:
            self.session_id = f"{self.exam_id}_user_{self.user.id}"
            EXAM_SESSIONS[self.exam_id][self.session_id] = {
                "violation_count": 0
            }

            await self.channel_layer.group_add(
                self.student_group,
                self.channel_name
            )

            await self.channel_layer.group_send(
                self.proctor_group,
                {
                    "type": "student_joined",
                    "masked_session_id": self.session_id[-6:],
                    "full_session_id": self.session_id,
                    "violation_count": 0,
                }
            )

        await self.accept()

        if self.is_proctor:
            await self.sync_existing_students()

    async def sync_existing_students(self):
        sessions = EXAM_SESSIONS.get(self.exam_id, {})
        for session_id, data in sessions.items():
            await self.send(text_data=json.dumps({
                "type": "student_joined",
                "masked_session_id": session_id[-6:],
                "full_session_id": session_id,
                "violation_count": data["violation_count"],
            }))

    async def disconnect(self, close_code):
        if self.is_proctor:
            await self.channel_layer.group_discard(
                self.proctor_group,
                self.channel_name
            )
        else:
            await self.channel_layer.group_discard(
                self.student_group,
                self.channel_name
            )
            EXAM_SESSIONS[self.exam_id].pop(self.session_id, None)

    async def receive(self, text_data):
        if self.is_proctor:
            return

        data = json.loads(text_data)

        if data.get("type") == "tab_change":
            session = EXAM_SESSIONS[self.exam_id].get(self.session_id)
            if not session:
                return

            session["violation_count"] += 1
            await self.log_tab_change()


            await self.channel_layer.group_send(
                self.proctor_group,
                {
                    "type": "violation_update",
                    "masked_session_id": self.session_id[-6:],
                    "full_session_id": self.session_id,
                    "violation_count": session["violation_count"],
                }
            )

    async def student_joined(self, event):
        if not self.is_proctor:
            return

        await self.send(text_data=json.dumps({
            "type": "student_joined",
            "masked_session_id": event["masked_session_id"],
            "full_session_id": event["full_session_id"],
            "violation_count": event["violation_count"],
        }))

    async def violation_update(self, event):
        if not self.is_proctor:
            return

        await self.send(text_data=json.dumps({
            "type": "violation_update",
            "masked_session_id": event["masked_session_id"],
            "full_session_id": event["full_session_id"],
            "violation_count": event["violation_count"],
        }))