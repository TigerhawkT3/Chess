import time

class TimeControl(object):
    """
    A time control module. Allows for the following modes:
        Basic: each player starts with a fixed time period. Being the active player
            decreases available time. No special calculations.
        Hourglass: each player starts with a fixed time period. Being the active
            player decreases available time. Being the inactive player increases
            available time.
        Bronstein: each player starts with a fixed time period. When it becomes
            a player's turn, they can move within a fixed delay period to avoid
            consuming any time. If their move time exceeds the delay, play appears
            the same as Basic mode.
        Fischer: each player starts with a fixed time period. When it becomes a
            player's turn, a fixed delay period is added to their available time.
            Unused time is accumulated.
        Byo-Yomi: each player starts with a fixed time period and a series of
            fixed 'byo-yomi' time periods. When it becomes a player's turn,
            byo-yomi time periods are consumed one at a time as the move time
            grows beyond them. When there are no byo-yomi periods left, move time
            begins to consume the original fixed time period.
    Parameters:
        kwargs:
            p1time: number of p1 seconds
            p2time: number of p2 seconds
            mode: game mode, can be 'hourglass', 'bronstein', 'fischer', 'byoyomi', or None
            p1_byo_yomi: list of player 1 byo yomi periods
            p2_byo_yomi: list of player 2 byo yomi periods
        p1time (float): initial base time for player 1
        p2time (float): initial base time for player 2
        turn (int): whose turn it is. 0 for paused, 1 for player 1, 2 for player 2
        lastturn (int): whose turn it was when the timer was paused
        start_time (float): the monotonic time when the timer was started
        p1current (float): player 1's remaining main time, calculated from the last event
        p2current (float): player 2's remaining main time, calculated from the last event
        delay (float): the chosen delay for bronstein or fischer modes
        p1_delay (float): the remaining time in player 1's bronstein delay period (used for pause purposes)
        p2_delay (float): the remaining time in player 2's bronstein delay period (used for pause purposes)
        mode (string or None): 'hourglass', 'bronstein', 'fischer', 'byoyomi', or None
        p1_byo_yomi (list): a list of available byo-yomi periods for player 1
        p2_byo_yomi (list): a list of available byo-yomi periods for player 2
        savedbyo (float): the remaining time in the current byo-yomi period
        last_event (float): the time when the last event occurred
        change (float): a saved time differential
        
    To use this module, create a TimeControl object and pass it the proper keywords. Examples:
    
    import timecontrol as tc
    
    Make a normal timer with default times (1 hour per player):
        mytimer = tc.TimeControl()
    Make a normal timer with specified times (10 minutes each in this example):
        mytimer = tc.TimeControl(p1time=600, p2time=600)
    Make an hourglass timer with specified times (10 minutes each in this example):
        mytimer = tc.TimeControl(p1time=600, p2time=600, mode='hourglass')
    Make a Bronstein delay timer with default times and a delay of 30 seconds:
        mytimer = tc.TimeControl(mode='bronstein', delay=30)
    Make a Fischer delay timer with default times and a delay of 30 seconds:
        mytimer = tc.TimeControl(mode='fischer', delay=30)
    Make a Byo-Yomi timer with default times and 3 byo-yomi periods of 1 minute each, for each player:
        mytimer = tc.TimeControl(mode='byoyomi', p1_byo_yomi=[60,60,60], p2_byo_yomi=[60,60,60])
    """
    def __init__(self, **kwargs):
        if not kwargs.get('p1time'):
            kwargs['p1time'] = 3600
        if not kwargs.get('p2time'):
            kwargs['p2time'] = 3600
        
        self.p1time = self.p1current = kwargs.get('p1time') # int (in seconds)
        self.p2time = self.p2current = kwargs.get('p2time') # int (in seconds)
                
        self.turn = 1 # 0 for paused, 1 for p1, 2 for p2
        self.start_time = self.last_event = 0
        
        self.delay = self.p1_delay = self.p2_delay = None # a number, or None
        self.p1_byo_yomi = kwargs.get('p1_byo_yomi')
        self.p2_byo_yomi = kwargs.get('p2_byo_yomi')
        if kwargs.get('bronstein'):
            self.mode = 'bronstein'
            self.delay = self.p1_delay = self.p2_delay = kwargs.get('bronstein')
        elif kwargs.get('fischer'):
            self.mode = 'fischer'
            self.delay = self.p1_delay = self.p2_delay = kwargs.get('fischer')
        elif kwargs.get('hourglass'):
            self.mode = 'hourglass'
        elif self.p1_byo_yomi or self.p2_byo_yomi:
            self.mode = 'byoyomi'
        else:
            self.mode = None
        
    def start(self):
        """
        Starts the timer.
        """
        if self.mode in ('bronstein', 'fischer'): # if there's any kind of delay,
            self.p1current += self.delay # add it
        self.start_time = self.last_event = time.monotonic()
        if self.p1_byo_yomi:
            self.savedbyo = self.p1_byo_yomi[0]
        
    def switch(self):
        """
        Switches back and forth between player 1 and player 2. This is where
        timing calculations are carried out.
        """
        nowtime = time.monotonic()
        change = nowtime - self.last_event
        self.last_event = nowtime
        if self.turn == 1:
            self.turn = 2
            if self.mode == 'byoyomi':
                if self.p1_byo_yomi:
                    try:
                        while change > self.p1_byo_yomi[0]:
                            try:
                                change -= self.p1_byo_yomi.pop(0)
                            except:
                                self.p1current -= change
                        self.p1_byo_yomi[0] = self.savedbyo
                    except:
                        self.p1current -= change
                else:
                    self.p1current -= change
                if self.p2_byo_yomi:
                    self.savedbyo = self.p2_byo_yomi[0]
            elif self.mode == 'bronstein':
                self.p2current += self.delay
                self.p1current -= max(self.delay, change+self.delay-self.p1_delay)
                self.p2_delay = self.delay
            elif self.mode == 'fischer':
                self.p2current += self.delay
                self.p1current -= change
            elif self.mode == 'hourglass':
                self.p2current += change
                self.p1current -= change
            else: # no special mode
                self.p1current -= change
        elif self.turn == 2:
            self.turn = 1
            if self.mode == 'byoyomi':
                if self.p2_byo_yomi:
                    try:
                        while change > self.p2_byo_yomi[0]:
                            try:
                                change -= self.p2_byo_yomi.pop(0)
                            except:
                                self.p2current -= change
                        self.p2_byo_yomi[0] = self.savedbyo
                    except:
                        self.p2current -= change
                else:
                    self.p2current -= change
                if self.p2_byo_yomi:
                    self.savedbyo = self.p2_byo_yomi[0]
            elif self.mode == 'bronstein':
                self.p1current += self.delay
                self.p2current -= max(self.delay, change+self.delay-self.p2_delay)
                self.p1_delay = self.delay
            elif self.mode == 'fischer':
                self.p1current += self.delay
                self.p2current -= change
            elif self.mode == 'hourglass':
                self.p1current += change
                self.p2current -= change
            else: # no special mode
                self.p2current -= change
        # do not switch while paused
    
    def pause(self):
        """
        Pauses the timer. Works as a sort of switch to no one, saving some
        events just to keep track of things.
        """
        nowtime = time.monotonic()
        change = nowtime - self.last_event
        
        if self.turn == 1:
            if self.p1_byo_yomi:
                try:
                    while change > self.p1_byo_yomi[0]:
                        try:
                            change -= self.p1_byo_yomi.pop(0)
                        except:
                            self.p1current -= change
                    self.p1_byo_yomi[0] -= change
                except:
                    self.p1current -= change
            elif self.mode == 'bronstein':
                self.p1_delay -= change
            else:
                self.p1current -= change
            if self.mode == 'hourglass':
                self.p2current += change
            self.turn = 0
            self.lastturn = 1
        elif self.turn == 2:
            if self.p2_byo_yomi:
                try:
                    while change > self.p2_byo_yomi[0]:
                        try:
                            change -= self.p2_byo_yomi.pop(0)
                        except:
                            self.p2current -= change
                    self.p2_byo_yomi[0] -= change
                except:
                    self.p2current -= change
            elif self.mode == 'bronstein':
                self.p2_delay -= change
            else:
                self.p2current -= change
            if self.mode == 'hourglass':
                self.p1current += change
            self.turn = 0
            self.lastturn = 2
        else:
            self.turn = self.lastturn
        
        self.last_event = nowtime
        self.change = change

    def add_time(self, player, time):
        """
        Adds the specified time in seconds to the specified player's main time.
        Parameters:
            player (int): 1 for player 1, 2 for player 2
            time (float): number of seconds to add to that player's main time.
                Can be a fractional number.
        """
        if player == 1:
            self.p1current += time
        else:
            self.p2current += time
        
    @property
    def p1_remaining(self):
        """
        A property that returns the remaining time for player 1 as a float.
        """
        if self.turn == 1:
            if self.mode == 'bronstein':
                return self.p1current + self.last_event - time.monotonic() + self.p1_delay - 2*self.delay
            else:
                return self.p1current + self.last_event - time.monotonic()
        elif self.turn == 0:
            if self.mode == 'bronstein' and self.lastturn == 1:
                return self.p1current + self.p1_delay - 2*self.delay
            else:
                return self.p1current
        else:
            if self.mode == 'hourglass':
                return self.p1current + time.monotonic() - self.last_event
            else:
                return self.p1current
        
    @property
    def p2_remaining(self):
        """
        A property that returns the remaining time for player 2 as a float.
        """
        if self.turn == 2:
            if self.mode == 'bronstein':
                return self.p2current + self.last_event - time.monotonic() + self.p2_delay - 2*self.delay
            else:
                return self.p2current + self.last_event - time.monotonic()
        elif self.turn == 0:
            if self.mode == 'bronstein' and self.lastturn == 2:
                return self.p2current + self.p2_delay - 2*self.delay
            else:
                return self.p2current
        else:
            if self.mode == 'hourglass':
                return self.p2current + time.monotonic() - self.last_event
            else:
                return self.p2current
