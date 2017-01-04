class Progress:
    """
    Simple progress bar for use in a terminal shell
    """
    def __init__(self, x, shell):
        self.w = shell.width - 10
        self.x = x
        self.bar = ['[', '', '-' * (self.w - 1), '] ', '0', '%']
        self.i = 0
        self.j = int(float(self.i) / self.x * self.w)

    def __str__(self):
        return ''.join(self.bar)

    def step(self):
        self.i += 1
        self.j = int(float(self.i) / self.x * self.w)
        self.bar[1] = '#' * self.j
        self.bar[2] = '-' * (self.w - self.j)
        self.bar[4] = str(int(float(self.j) / self.w * 100))
