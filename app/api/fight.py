from api import models, serializers
import random, decimal


class Fight:

    def __init__(self):
        self.last_strike_critical = False
        self.damage_dealt = 0

    def calculate_critical_hit(self, attacker):
        rand = decimal.Decimal(str(random.uniform(0,1)))
        is_critical = attacker.criticalHitChance >= rand
        self.last_strike_critical = is_critical
        damage = attacker.damage * attacker.criticalHitDamage if is_critical else attacker.damage
        return damage

    def perform_attack(self, attacker, defender):
        hit_dmg = Fight.calculate_critical_hit(self, attacker=attacker)
        dmg = hit_dmg - defender.armor if hit_dmg - defender.armor > 0 else 0
        self.damage_dealt = int(dmg)
        print(self.damage_dealt)
        defender.health -= dmg

        return {attacker: attacker, defender: defender}
    
    def handle_fight(attacker, defender, user_turn):
        attacker_stats = attacker
        print(attacker_stats)
        defender_stats = defender

        if user_turn:
            Fight.perform_attack(attacker_stats, defender_stats)
        else:
            Fight.perform_attack(defender_stats, attacker_stats)
        
        return {attacker: attacker_stats, defender: defender_stats}

    @staticmethod
    def get_loot(enemy: models.Enemy):
        loots = models.EnemyLoot.objects.filter(enemy=enemy)
        strike = random.random()
        counter = 0.0
        for loot in loots:
            counter += loot.rarity
            if strike <= counter:
                item = serializers.ItemSerializer(loot.item).data
                return item
        
        return None
    
    @staticmethod
    def get_exp(enemy: models.Enemy):
        return enemy.exp
