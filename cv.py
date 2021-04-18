from __future__ import with_statement
from threading import Thread, Lock, Condition, Semaphore
from os import _exit as quit
import time, random

####################################################### 
#                      
# Partner 1: Indiana Huey
#
# Partner 2: Samuel Nunoo
# 
#######################################################


# Modify only the code of the class Club to make the program
# correct.

# Place your synchronization variables inside the Club instance.

# Make sure nobody is holding a Club synchronization variable
# while executing outside the Club code.

# init lock and cv's
lock = Lock()
goth_friendly = Condition(lock)
hipster_friendly = Condition(lock)

# Too 
def hangout():
    time.sleep(random.randint(0, 2))


class Club:
    def __init__(self, capacity):
        self.goth_count = 0               # num goths in club
        self.hipster_count = 0            # num hipsters in club
        self.capacity = capacity          # only used for optional questions

        self.consec_goths = 0             # num consecutive goths joined
        self.consec_hipsters = 0;         # num consecutive hipsters joined
        self.max_consec = 3               # num consecutive allowed

           
    def __sanitycheck(self):
        if self.goth_count > 0 and self.hipster_count > 0:
            print("sync error: bad social mixup! Goths = %d, Hipsters = %d" %  (self.goth_count, self.hipster_count))
            quit(1)
        if self.goth_count>self.capacity or self.hipster_count>self.capacity:
            print("sync error: too many people in the club! Goths = %d, Hipsters = %d" %  (self.goth_count, self.hipster_count))
            quit(1)
        if self.goth_count < 0 or self.hipster_count < 0:
            print("sync error: lost track of people! Goths = %d, Hipsters = %d" %  (self.goth_count, self.hipster_count))
            quit(1)

        
    def goth_enter(self):
        lock.acquire()

        # wait while there are hipsters, too many goths have joined consecutively, or club is at capacity
        while self.hipster_count > 0 or self.consec_goths >= self.max_consec or self.goth_count >= self.capacity:
            goth_friendly.wait()

        self.goth_count += 1               
        self.consec_goths += 1
        self.__sanitycheck()
        lock.release()


    def goth_exit(self):
        lock.acquire()

        self.goth_count -= 1

        # notify all hipsters if all goths have left, otherwise notify a goth
        if self.goth_count == 0:
            self.consec_goths = 0;
            hipster_friendly.notify_all()
        else:
            goth_friendly.notify()

        self.__sanitycheck()
        lock.release()


    def hipster_enter(self):
        lock.acquire()

        # wait while there are goths, too many hipsters have joined consecutively, or club is at capacity
        while self.goth_count > 0 or self.consec_hipsters >= self.max_consec or self.hipster_count >= self.capacity:
            hipster_friendly.wait()

        self.hipster_count += 1
        self.consec_hipsters += 1
        self.__sanitycheck()
        lock.release()

        
    def hipster_exit(self):
        lock.acquire()

        self.hipster_count -= 1

        # notify all goths if all hipsters have left, otherwise notify a hipster
        if self.hipster_count == 0:
            self.consec_hipsters = 0;
            goth_friendly.notify_all()
        else:
            hipster_friendly.notify()

        self.__sanitycheck()                  
        lock.release()


class Goth(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        global daclub

        while True:
            print("goth #%d: wants to enter" % self.id)
            daclub.goth_enter()
            print("goth #%d: in the club" % self.id)
            print("goths in club: %d" % daclub.goth_count)
            hangout()
            daclub.goth_exit()
            print("goth #%d: left club" % self.id)
            print("goths in club: %d" % daclub.goth_count)
            
class Hipster(Thread):
    def __init__(self, id):
        Thread.__init__(self)
        self.id = id

    def run(self):
        global daclub

        while True:
            print("hipster #%d: wants to enter" % self.id)
            daclub.hipster_enter()
            print("hipster #%d: in the club" % self.id)
            print("hipsters in club: %d" % daclub.hipster_count)
            hangout()
            daclub.hipster_exit()
            print("hipster #%d: left club" % self.id)
            print("hipsters in club: %d" % daclub.hipster_count)


NUMGOTH = 3
NUMHIPSTER = 3
CAPACITY = NUMGOTH + NUMHIPSTER
daclub = Club(CAPACITY)


def main():
    for i in range(0, NUMGOTH):
        g = Goth(i)
        g.start()    
    for i in range(0, NUMHIPSTER):
        h = Hipster(i)
        h.start()    

if __name__ == "__main__":
    main()

#@note : 