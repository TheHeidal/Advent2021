

class Step:
    """
    A step in the reboot sequence
    """

    def __init__(self, state, xmin, xmax, ymin, ymax, zmin, zmax):
        self.state = state == 'on'
        self.x_range = range(int(xmin), int(xmax) + 1)
        self.y_range = range(int(ymin), int(ymax) + 1)
        self.z_range = range(int(zmin), int(zmax) + 1)

    def __repr__(self):
        return (f"{'on' if self.state else 'off'} "
                f"x={self.x_range.start}..{self.x_range.stop - 1},"
                f"y={self.y_range.start}..{self.y_range.stop - 1},"
                f"z={self.z_range.start}..{self.z_range.stop - 1}")


class IntervalContainer:
    def __init__(self, start, stop, *other_indices):
        self.first = Interval(self, start, stop, *other_indices)
        self.last = self.first

    @staticmethod
    def insert_behind(existing_interval, new_interval):
        """insert new_interval behind interval in the linked list"""
        assert existing_interval.container is new_interval.container
        if existing_interval.start == new_interval.stop + 1:
            existing_interval.start = new_interval.start
            del new_interval
            if existing_interval.prev is not None and existing_interval.start == existing_interval.prev.stop + 1:
                IntervalContainer.merge(existing_interval.prev, existing_interval)
        else:
            if existing_interval.prev is None:
                new_interval.next = existing_interval
                existing_interval.prev = new_interval
                existing_interval.container.first = new_interval
            else:
                temp = existing_interval.prev
                temp.next = new_interval
                new_interval.prev = temp
                new_interval.next = existing_interval
                existing_interval.prev = new_interval

    @staticmethod
    def insert_ahead(existing_interval, new_interval):
        """insert new_interval ahead of interval in the linked list"""
        assert existing_interval.container is new_interval.container
        if existing_interval.stop + 1 == new_interval.start:
            existing_interval.stop = new_interval.stop
            del new_interval
            if existing_interval.next is not None \
                    and existing_interval.stop + 1 == existing_interval.next.start \
                    and existing_interval.subcontainer == existing_interval.next.subcontainer:
                IntervalContainer.merge(existing_interval, existing_interval.next)
        else:
            if existing_interval.next is None:
                existing_interval.next = new_interval
                new_interval.prev = existing_interval
                existing_interval.container.last = new_interval
            else:
                IntervalContainer.connect(new_interval, existing_interval.next)
                IntervalContainer.connect(existing_interval, new_interval)

    @staticmethod
    def merge(prev_interval, post_interval):
        """merges the post-interval into the prev-interval and then deletes the post-interval"""
        assert prev_interval.container is post_interval.container
        assert prev_interval.stop + 1 == post_interval.start
        assert prev_interval.subcontainer == post_interval.subcontainer
        prev_interval.stop = post_interval.stop
        IntervalContainer.connect(prev_interval, post_interval.next)
        if post_interval.container.last == post_interval:
            prev_interval.container.last = prev_interval
        del post_interval

    @staticmethod
    def connect(prev_interval, post_interval):
        if prev_interval is not None:
            prev_interval.next = post_interval
        if post_interval is not None:
            post_interval.prev = prev_interval

    def update(self, state, start, stop, *other_indices):
        self._update(self.first, state, start, stop, *other_indices)

    def _update(self, curr_interval, state: bool, update_start: int, update_stop: int, *other_indices):
        """tries to apply (state, start, stop) to all intervals in _data[start_i:]"""
        while curr_interval is not None:
            if update_start < curr_interval.start:
                if update_stop < curr_interval.start:
                    if state:
                        self.insert_behind(curr_interval,
                                           Interval(self, update_start, update_stop, *other_indices))
                        # if the update is entirely behind curr_interval, we create a new interval to deal with it
                else:
                    if state:
                        self.insert_behind(curr_interval,
                                           Interval(self, update_start, curr_interval.start - 1, *other_indices))
                    update_start = curr_interval.start
                    # if the update starts behind but overlaps with curr_interval
                    #   we split it into the non-overlapping parts and overlapping parts
                    #   non-overlapping part gets added behind curr_interval
                    #   overlapping part is treated as a new update that necessarily will apply to curr_part
            else:
                if update_stop <= curr_interval.stop:
                    # If the update is entirely within the next
                    curr_interval.update(state, update_start, update_stop, *other_indices)
                    return
                else:
                    if update_start <= curr_interval.stop:
                        curr_interval.update(state, update_start, curr_interval.stop, *other_indices)
                        update_start = curr_interval.stop + 1
                    curr_interval = curr_interval.next
        if state:
            self.insert_ahead(self.last, Interval(self, update_start, update_stop))

    def list(self):
        return [i.list() for i in self]

    def __iter__(self):
        return LinkedListIterator(self.first)

    def __repr__(self):
        return f"""[{",".join(str(a) for a in self)}]"""

    def __eq__(self, other):
        s_curr_interval = self.first
        o_curr_interval = other.first
        while s_curr_interval is not None and o_curr_interval is not None:
            curr = s_curr_interval == o_curr_interval
            if not curr:
                return curr
            s_curr_interval = s_curr_interval


class Interval:
    def __init__(self, container: IntervalContainer, start: int, stop: int, *other_indices):
        self.container = container
        self.start = start
        self.stop = stop
        self.prev = None
        self.next = None
        if len(other_indices) != 0:
            self.subcontainer = IntervalContainer(*other_indices)
        else:
            self.subcontainer = None

    def contains(self, index):
        return self.start <= index <= self.stop

    def update(self, state, update_start, update_stop, *other_indices):
        assert self.contains(update_start)
        assert self.contains(update_stop)
        if self.subcontainer is not None:
            if len(other_indices) != 0:
                self.subcontainer.update(state, *other_indices)
            else:
                raise IndexError("did not give enough indices")
        if not state:
            if update_start == self.start:
                if update_stop == self.stop:
                    self.delete()
                else:
                    self.start = update_stop + 1
            else:
                if update_stop == self.stop:
                    self.start = update_start
                else:
                    new_interval = Interval(self.container, self.start, update_start - 1)
                    self.start = update_stop + 1
                    self.container.insert_behind(self, new_interval)

    def delete(self):
        if self.prev is not None:
            self.prev.next = self.next
        else:
            self.container.first = self.next
        if self.next is not None:
            self.next.prev = self.prev
        else:
            self.container.last = self.prev

    def list(self):
        if self.subcontainer is None:
            return [i for i in range(self.start, self.stop + 1)]
        else:
            return [[a] + b for a in range(self.start, self.stop + 1) for b in self.subcontainer.list()]

    def __eq__(self, other):
        curr = self.start == other.start and self.stop == other.stop
        if self.subcontainer is not None:
            return curr and self.subcontainer == other.subcontainer
        return curr

    def __repr__(self):
        if self.subcontainer is not None:
            return f"({self.start}..{self.stop}<{self.subcontainer}>)"
        else:
            return f"({self.start}..{self.stop})"


class LinkedListIterator:

    def __init__(self, head):
        self._current = head

    def __iter__(self):
        return self

    def __next__(self):
        if self._current is None:
            raise StopIteration
        temp = self._current
        self._current = self._current.next
        return temp

# if __name__ == '__main__':
#     steps = [Step(*s) for s in read_input('D22test1.txt')]
#     reactor = Reactor()
#     pass
