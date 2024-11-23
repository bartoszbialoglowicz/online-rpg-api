import json
from channels.generic.websocket import WebsocketConsumer
from django.forms.models import model_to_dict

from api import models
from api.fight import Fight

class CombatSystemConsumer(WebsocketConsumer):
    def connect(self):
            self.user = None
            self.enemy = None
            self.accept()

    def disconnect(self, close_code):
        # Leave the room group
        self.close()
    
    def receive(self, text_data):
        
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if 'type' in message and message['type'] == 'set_enemy':
            self.enemy = models.Enemy.objects.get(id=message['enemyId'])
        if 'type' in message and message['type'] == 'set_user':
            user_id = models.CustomUser.objects.get(email=message['userEmail'])
            self.user = models.Character.objects.get(user=user_id)
        if 'action' in message and message['action'] == 'user_attack':
            self.user, self.enemy = Fight.normal_attack(self.user, self.enemy, True)
            self.send(text_data=json.dumps({'character': model_to_dict(self.user)}))
            print(model_to_dict(self.enemy, exclude=['imgSrc']))
            self.send(text_data=json.dumps({'enemy': model_to_dict(self.enemy, exclude=['imgSrc'])}))
            if self.enemy.health <= 0:
                # Get item loot
                loot = Fight.get_loot(self.enemy)
                # Add exp to resurces model
                models.Resources.objects.get(user=self.user.user).add_exp(self.enemy.exp)
                # Get new user's lvl
                lvl = models.Resources.objects.get(user=self.user.user).lvl.lvl
                # Get user's current lvl exp needed to next lvl
                expPoints = models.UserLvl.objects.get(lvl=lvl).expPoints
                # Send messege back to user
                self.send(text_data=json.dumps({
                    'message': 'You won the fight',
                    'fightIsOver': True,
                    'loot': loot[0],
                    'exp': self.enemy.exp,
                    'lvl': lvl,
                    'expPoints': expPoints,
                    'strike': loot[1]
                }))
                self.close()

        if 'action' in message and message['action'] == 'enemy_attack':
            self.user, self.enemy = Fight.normal_attack(self.user, self.enemy, False)
            self.send(text_data=json.dumps({'character': model_to_dict(self.user)}))
            self.send(text_data=json.dumps({'enemy': model_to_dict(self.enemy, exclude=['imgSrc'])}))
            if self.user.health <= 0:
                self.send(text_data=json.dumps({
                    'message': 'You lost the fight',
                    'fightIsOver': True,
                }))
                self.close()