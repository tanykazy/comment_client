# -*- coding: utf_8 -*-


__all__ = [""]


from define import MultiThreadClass
from define import MessageBox
from define import EventId
from define import UnitId
from define import Wrapper
from define import Unique


class TimerMng(MultiThreadClass):
    """
    Timer
    """
    def __init__(self, daemon=False):

        self.__STATE_IDLE = 0x00

        matrix = {
            EventId.TIMERREQ: {
                self.__STATE_IDLE: self.__idle_timerreq}}

        MultiThreadClass.__init__(
            self,
            name=__name__,
            uniid=UnitId.TIMERMNG,
            matrix=matrix,
            daemon=daemon)

        self.state = self.__STATE_IDLE

        self.__timer_list = dict()
        self.__timer_list_lock = Wrapper.Lock()

    def kill(self):
        self.log.trace()
        for timer_id in self.__timer_list:
            self.__timer_list[timer_id].cancel()
        self.__timer_list.clear()
        MultiThreadClass.kill(self)

    def __timer_expire(self, timer_id, unit_id=None, event_id=None, data=None):
        self.log.trace()
        result = self.send_message(
            unit = unit_id,
            event = event_id,
            data = data)
        self.__timer_list_lock.acquire(blocking = True, timeout = -1)
        del self.__timer_list[timer_id]
        self.__timer_list_lock.release()

    def __idle_timerreq(self, container):
        self.log.trace()
        self.__timer_list_lock.acquire(blocking = True, timeout = -1)
        timer_id = Unique.unique()
        timer = Wrapper.Timer(
            interval = container.message.interval,
            function = self.__timer_expire,
            args = None,
            kwargs = {
                "timer_id": timer_id,
                "unit_id": container.message.unit_id,
                "event_id": container.message.event_id,
                "data": container.message.data})
        self.__timer_list[timer_id] = timer
        self.__timer_list[timer_id].start()
        self.__timer_list_lock.release()
        return True


if __name__ == "__main__":
    pass


