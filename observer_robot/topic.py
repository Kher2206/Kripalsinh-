"""The observer pattern in its smallest form, using ROS2 vocabulary.

    Observer pattern        ROS2
    ----------------        ----------------------------
    Subject                 Topic
    attach(observer)        create_subscription(callback)
    detach(observer)        destroy_subscription(...)
    notify(data)            publisher.publish(msg)
    Observer.update(data)   the subscription callback
"""

class Topic:
    """A named channel (the *subject*). Subscribers are plain callables (the *observers*)."""

    def __init__(self, name):
        self.name = name
        self._callbacks = []

    def subscribe(self, callback):
        """Register a function that is called with every published message."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def publish(self, msg):
        """Notify all subscribers. The publisher does not know who is listening."""
        for callback in list(self._callbacks):
            callback(msg)

    def subscriber_count(self):
        return len(self._callbacks)
