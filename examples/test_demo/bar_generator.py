from typing import Callable

class BarGenerator_New:
    def __init__(
        self,
        on_bar: Callable,
        window: int, 
        on_window_bar: Callable 
        ):
        # 存储未完成的K线数据
        self.bar: int = 0 
        self.on_bar = on_bar
        self.window = window
        self.on_window_bar = on_window_bar
        self.window_bar: int = 0
    
    def update_tick(self, tick):
        if not self.bar:
            self.bar = tick
        else:
            self.bar += tick
        
        if self.bar == 10:
            self.on_bar(self.bar)
            self.bar = 0
    
    def update_bar(self, bar):
        if not self.window_bar:
            self.window_bar = bar
        else:
            self.window_bar += bar 
        
        if self.window_bar == 50:
            self.on_window_bar(self.window_bar)
            self.window_bar = 0

class Tem:
    def __init__(self):
        self.bg = BarGenerator_New(self.on_bar, 5, self.on_5min_bar)
    
    def on_tick(self, tick: int):
        self.bg.update_tick(tick)

    def on_bar(self, bar: int):
        print(f"合成了一根k线{bar}")
        self.bg.update_bar(bar)
    
    def on_5min_bar(self, bar: int):
        print(f"合成了一根5minK线{bar}")

a = Tem()
for i in range(50):
    a.on_tick(i)