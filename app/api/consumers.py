import json
from channels.generic.websocket import WebsocketConsumer
from django.forms.models import model_to_dict

from api import models
from api import serializers
from api.fight import Fight

class CombatSystemConsumer(WebsocketConsumer):
    def connect(self):
            self.user = None
            self.userTurnDone = True
            self.enemyTurnDone = True
            self.enemy = None
            self.winner = False
            self.loot = None
            self.lvl = None
            self.expPoints = None
            self.exp = None
            self.fightInfo = Fight()
            self.accept()

    def disconnect(self, close_code):
        # Leave the room group
        self.close()

    def handle_user_attack(self):
        self.userTurnDone = False
        self.user, self.enemy = self.fightInfo.perform_attack(self.user, self.enemy)
        self.send_enemy_update()
        self.userTurnDone = True

        if self.enemy.health <= 0:
            self.winner = True
            self.handle_fight_end()
    
    def handle_enemy_attack(self):
        self.enemyTurnDone = False
        self.enemy, self.user = self.fightInfo.perform_attack(self.enemy, self.user)
        self.send_character_update()
        self.enemyTurnDone = True

        if self.user.health <= 0:
            self.winner = False
            self.handle_fight_end()

    def update_user_lvl(self):
        models.Resources.objects.get(user=self.user.user).add_exp(self.enemy.exp)
        self.lvl = models.Resources.objects.get(user=self.user.user).lvl.lvl
        # Get user's current lvl exp needed to next lvl
        self.expPoints = models.UserLvl.objects.get(lvl=self.lvl).expPoints
        # Get user's current exp points
        self.exp = models.Resources.objects.get(user=self.user.user).exp

    def handle_fight_end(self):
        if self.winner:
            self.loot = Fight.get_loot(self.enemy)
            self.update_user_lvl()
        
        self.send_fight_data()
        self.close()

    def send_character_update(self):
        self.send(text_data=json.dumps({'character': serializers.CharacterSerializer(self.user).data, 'criticalHit': self.fightInfo.last_strike_critical}))
    
    def send_enemy_update(self):
        self.send(text_data=json.dumps({'enemy': serializers.EnemySerializer(self.enemy).data, 'criticalHit': self.fightInfo.last_strike_critical}))

    def send_fight_data(self):
        msg = "You won the fight" if self.winner else "You lost the fight"
        self.send(text_data=json.dumps({
            'message': msg,
            'fightIsOver': True,
            'loot': self.loot,
            'exp': self.exp,
            'lvl': self.lvl,
            'expPoints': self.expPoints
        }))

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
            if self.userTurnDone:
                self.handle_user_attack()

        if 'action' in message and message['action'] == 'enemy_attack':
            if self.enemyTurnDone:
                self.handle_enemy_attack()