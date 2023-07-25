from api import models
import random

class Fight:
    def normal_attack(user: models.Character, enemy: models.Enemy, user_turn: bool):
        user_stats = user
        enemy_stats = enemy

        if user_turn:
            dmg = user_stats.damage - enemy_stats.armor
            if enemy_stats.armor > user_stats.damage:
                dmg = 0
            enemy_stats.hp = enemy_stats.hp - dmg
        else:
            dmg = enemy_stats.damage - user_stats.armor
            if user_stats.armor > enemy_stats.damage:
                dmg = 0
            user_stats.health = user_stats.health - dmg
        
        return {user: user_stats, enemy: enemy_stats}
    
    def get_loot(enemy: models.Enemy):
        loots = models.EnemyLoot.objects.filter(enemy=enemy)
        strike = random.random()
        counter = 0.0
        for loot in loots:
            counter += loot.rarity
            if strike <= counter:
                return [loot.item.name, strike]
        
        return ['null', strike]