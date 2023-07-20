import json
from channels.generic.websocket import AsyncWebsocketConsumer
from api import models
from django.db.models import F


class CombatSystemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'combat_room'
        self.room_group_name = 'combat_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)

        if 'action' in data and data['action'] == 'attack':
            character = models.Character.objects.first()
            enemy = models.Enemy.objects.first()

            char_hp = character.health
            char_dmg = character.damage
            enemy_hp = enemy.hp
            enemy_dmg = enemy.damage

            enemy_hp = enemy_hp - char_dmg
            if enemy_hp <= 0:
                enemy_hp = 0
            
            char_hp = char_hp - enemy_dmg
            if char_hp <= 0:
                char_hp = 0
            
            updated_game_state = {
                'user': {
                    'hp': char_hp,
                    'damage': char_dmg
                },
                'enemy': {
                    'hp': enemy_hp,
                    'damage': enemy_dmg
                }
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'combat_message',
                    'message': json.dumps(updated_game_state),
                }
            )