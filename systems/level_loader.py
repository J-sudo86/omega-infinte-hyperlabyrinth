import json
from core.wall import Wall
from entities.enemy import Enemy
from entities.player import Player

class Level:
    def __init__(self,data):self.data=data
    def build(self):
        d=self.data
        walls=[Wall(*w) for w in d['walls']]
        p=Player(*d['player'])
        enemies=[Enemy(e['x'],e['y'],e.get('hp',20),e.get('speed',65),e.get('damage',10)) for e in d['enemies']]
        return p,walls,enemies

def load_levels(path='levels/levels.json'):
    with open(path,encoding='utf8') as f:return json.load(f)['levels']
