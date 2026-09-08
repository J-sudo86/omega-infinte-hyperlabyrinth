import heapq, math

class AStarGrid:
    """A* pathfinder over a grid. Walls are inflated by the actor radius."""
    def __init__(self, world_w, world_h, cell, walls, actor_radius=9):
        self.w=world_w; self.h=world_h; self.cell=cell
        self.cols=math.ceil(world_w/cell); self.rows=math.ceil(world_h/cell)
        self.walls=walls; self.radius=actor_radius
        self.blocked=set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self._blocked(c,r): self.blocked.add((c,r))

    def _blocked(self,c,r):
        x=(c+0.5)*self.cell; y=(r+0.5)*self.cell
        return any(w.collides_circle((x,y),self.radius+self.cell*0.48) for w in self.walls)

    def cell_of(self,p):
        return int(p[0]//self.cell), int(p[1]//self.cell)
    def center(self,node):
        c,r=node; return ((c+0.5)*self.cell,(r+0.5)*self.cell)

    def neighbors(self,n):
        c,r=n
        for dc,dr,cost in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(-1,1,1.414),(1,-1,1.414),(-1,-1,1.414)):
            q=(c+dc,r+dr)
            if 0<=q[0]<self.cols and 0<=q[1]<self.rows and q not in self.blocked:
                # Prevent diagonal corner cutting.
                if dc and dr and ((c+dc,r) in self.blocked or (c,r+dr) in self.blocked): continue
                yield q,cost

    def find_path(self,start,end):
        s=self.cell_of(start); g=self.cell_of(end)
        if s in self.blocked or g in self.blocked: return []
        openq=[(0,s)]; came={}; gscore={s:0}
        while openq:
            _,cur=heapq.heappop(openq)
            if cur==g:
                path=[]
                while cur in came: path.append(self.center(cur)); cur=came[cur]
                path.append(self.center(s)); path.reverse(); return path
            for nxt,cost in self.neighbors(cur):
                score=gscore[cur]+cost
                if score < gscore.get(nxt,float('inf')):
                    came[nxt]=cur; gscore[nxt]=score
                    h=math.hypot(nxt[0]-g[0],nxt[1]-g[1])
                    heapq.heappush(openq,(score+h,nxt))
        return []
