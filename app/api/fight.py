from api import models, serializers
import random, decimal


class Fight:

    def __init__(self):
        self.last_strike_critical = False

    def calculate_critical_hit(self, attacker):
        rand = decimal.Decimal(str(random.uniform(0,1)))
        isCritical = attacker.criticalHitChance >= rand
        self.last_strike_critical = isCritical
        return attacker.damage * attacker.criticalHitDamage if isCritical else attacker.damage

    def perform_attack(self, attacker, defender):
        hitDmg = Fight.calculate_critical_hit(self, attacker=attacker)
        dmg = hitDmg - defender.armor if hitDmg - defender.armor > 0 else 0
        defender.health -= dmg

        return {attacker: attacker, defender: defender}
    
    def handle_fight(attacker, defender, user_turn):
        attacker_stats = attacker
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
